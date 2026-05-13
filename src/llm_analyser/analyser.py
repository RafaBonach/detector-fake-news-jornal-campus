import pandas as pd
import json
import numpy as np
from copy import deepcopy
from pathlib import Path
from dotenv import load_dotenv
import time
import concurrent.futures

from sklearn.metrics import precision_score, recall_score, f1_score # Métricas de avaliação

from config_base import MODELS, PROMPTS
from service_streamlit.utils import get_api_key

from groq import Groq

# --- Setup ---
load_dotenv()

class Analyser:
    def __init__(self, model_name):
        self.model_name = model_name
        self.api_key = get_api_key("groq_analyser")
        self.base_prompt = [
            {
                "role": "system",
                "content": PROMPTS["base"]["zero-shot"]
            }
        ]
        self.databases = {
            "fake-br": pd.read_csv("/home/rafael/Projetos/campus_multiplataforma_llm/src/database/Fake-Br/pre-processed_tratada.csv").sample(frac=1).reset_index(drop=True),
            "fake-recogna": [
                pd.read_csv("/home/rafael/Projetos/campus_multiplataforma_llm/src/database/FakeRecogna/FakeRecogna_no_removal_words_tratada.csv"),
                pd.read_csv("/home/rafael/Projetos/campus_multiplataforma_llm/src/database/FakeRecogna/FakeRecogna_tratada.csv")
            ]
        }
        self.df_results = pd.DataFrame()

        self.output_dir = Path("artifacts") / "analyser"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_path = self.output_dir / "df_results.csv"
        self.responses_path = self.output_dir / "responses.jsonl"

    def split_dataframe(
        self,
        dataframe: pd.DataFrame,
        max_rows: int = 32,
        max_estimated_tokens: int = 5999,
        text_column: str = "preprocessed_news",
    ) -> list[pd.DataFrame]:
        batches = []
        current_positions = []
        current_estimated_tokens = 0

        for position, text in enumerate(dataframe[text_column].astype(str).tolist()):
            estimated_tokens = max(1, len(text) // 4) + 40

            if current_positions and (
                len(current_positions) >= max_rows or current_estimated_tokens + estimated_tokens > max_estimated_tokens
            ):
                batches.append(dataframe.iloc[current_positions].copy())
                current_positions = []
                current_estimated_tokens = 0

            current_positions.append(position)
            current_estimated_tokens += estimated_tokens

        if current_positions:
            batches.append(dataframe.iloc[current_positions].copy())

        return batches

    def compute_intermediate_metrics(self) -> dict:
        valid = self.df_results.dropna(subset=["answers", "predictions"]) if "predictions" in self.df_results.columns else pd.DataFrame()
        if valid.empty:
            metrics = {"precision": None, "recall": None, "f1": None, "n": 0}
        else:
            precision = precision_score(valid["answers"], valid["predictions"], zero_division=0)
            recall = recall_score(valid["answers"], valid["predictions"], zero_division=0)
            f1 = f1_score(valid["answers"], valid["predictions"], zero_division=0)
            metrics = {"precision": float(precision), "recall": float(recall), "f1": float(f1), "n": int(len(valid))}

        metrics_path = self.output_dir / "metrics.json"
        with metrics_path.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(metrics, ensure_ascii=False) + "\n")

        return metrics

    def refine_upcoming_batches(self, batches: list[pd.DataFrame], start_index: int, per_batch_token_limit: int) -> list[pd.DataFrame]:
        # Analisa batches futuros e divide os que excedem limite estimado
        new_batches = []
        for j, b in enumerate(batches):
            if j < start_index:
                new_batches.append(b)
                continue

            # garante que temos um DataFrame; usa índices para dividir em DataFrames
            if not isinstance(b, pd.DataFrame):
                b = pd.DataFrame(b)

            def _split_df_into_parts(df_obj: pd.DataFrame, parts: int) -> list[pd.DataFrame]:
                idx_chunks = list(np.array_split(df_obj.index, parts))
                return [df_obj.loc[idxs].copy() for idxs in idx_chunks if len(idxs) > 0]

            prompt = self.build_prompt(b)
            est = self.estimate_messages_tokens(prompt)
            if est > per_batch_token_limit:
                # dividir até que cada pedaço fique abaixo do limite
                parts = 2
                splitted = _split_df_into_parts(b, parts)
                # se ainda exceder após uma divisão, continue dividindo
                while any(self.estimate_messages_tokens(self.build_prompt(s)) > per_batch_token_limit for s in splitted):
                    parts *= 2
                    splitted = _split_df_into_parts(b, parts)
                new_batches.extend(splitted)
            else:
                new_batches.append(b)

        return new_batches

    def estimate_messages_tokens(self, messages: list[dict]) -> int:
        # Estimativa simples: 1 token ~ 4 chars, adiciona overhead por mensagem
        total = 0
        for m in messages:
            content = str(m.get("content", ""))
            total += max(1, len(content) // 4) + 20
        # reserva para completions
        total += 100
        return total

    def build_prompt(self, batch_df: pd.DataFrame) -> list[dict]:
        prompt = deepcopy(self.base_prompt)

        for news_index, news_text in batch_df["preprocessed_news"].items():
            prompt.append({
                "role": "user",
                "content": f"{news_index}| {news_text}"
            })

        return prompt

    def chat_groq(self, messages: list[dict]):
        groq_client = Groq(api_key=self.api_key)

        response = groq_client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            temperature=0.7,
            response_format={ "type": "json_object" },
            seed=42,
        )

        return json.loads(response.choices[0].message.content)

    def save_checkpoint(self, raw_response: dict | None = None) -> None:
        self.df_results.to_csv(self.results_path, index=True)

        if raw_response is not None:
            with self.responses_path.open("a", encoding="utf-8") as file_handle:
                file_handle.write(json.dumps(raw_response, ensure_ascii=False) + "\n")

    def analyse(self):
        # Carrega todo o dataframe (pode ser ajustado para maior cobertura)
        df = self.databases["fake-br"]

        # Inicializa df_results com todos os índices do dataframe alvo
        self.df_results = pd.DataFrame(index=df.index)

        # Cria batches grandes (configuráveis) para reduzir número de requisições
        per_batch_token_limit = 4999
        batches = self.split_dataframe(df, max_rows=32, max_estimated_tokens=per_batch_token_limit, text_column="preprocessed_news")

        # Arquivo de cancelamento externo
        cancel_file = self.output_dir / "CANCEL"

        i = 0
        sent = 0
        # Executor para rodar tarefas durante o intervalo de espera
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            while i < len(batches):
                batch = batches[i]
                # Permite cancelamento externo antes de enviar
                if cancel_file.exists():
                    print("Cancelamento detectado: arquivo CANCEL presente. Interrompendo.")
                    break

                # Preenche rótulos verdadeiros
                self.df_results.loc[batch.index, "answers"] = batch["Classificação"]

                prompt = self.build_prompt(batch)

                # Verifica estimativa de tokens do prompt e, se exceder, divide o batch em 2
                est = self.estimate_messages_tokens(prompt)
                if est > per_batch_token_limit:
                    print(f"Batch atual estimado em {est} tokens (> {per_batch_token_limit}), dividindo...")
                    # divide usando índices para garantir DataFrames
                    idx_chunks = list(np.array_split(batch.index, 2))
                    sub_batches = [batch.loc[idxs].copy() for idxs in idx_chunks if len(idxs) > 0]
                    batches[i:i+1] = sub_batches
                    # não incrementa i — processa o novo batch no mesmo índice
                    continue

                try:
                    response = self.chat_groq(prompt)
                except KeyboardInterrupt:
                    print("Execução interrompida pelo usuário (KeyboardInterrupt). Salvando checkpoint e saindo.")
                    self.save_checkpoint()
                    break
                except Exception as exc:
                    # Salva o que já foi processado e interrompe
                    self.save_checkpoint()
                    print(f"Erro ao consultar Groq: {exc}")
                    break

                # Armazena predições retornadas
                for item in response.get("classification_analysis", []):
                    try:
                        idx = int(item.get("news_index"))
                    except Exception:
                        idx = item.get("news_index")
                    self.df_results.loc[idx, "predictions"] = item.get("classification")

                # Salva checkpoint incremental e resposta bruta
                self.save_checkpoint({
                    "batch_index": int(batch.index.min()),
                    "batch_size": int(len(batch)),
                    "response_summary": {
                        "has_classification_analysis": "classification_analysis" in response,
                    },
                })

                sent += 1
                total = len(batches)
                remaining = total - sent
                print(f"Batches enviados: {sent} / {total}. Batches restantes: {remaining}.")

                # Durante o intervalo, executa tarefas em paralelo: recalcula métricas e refina batches futuros
                interval = 60
                future_metrics = executor.submit(self.compute_intermediate_metrics)
                future_refine = executor.submit(self.refine_upcoming_batches, batches, i+1, per_batch_token_limit)

                start_wait = time.time()
                while time.time() - start_wait < interval:
                    if cancel_file.exists():
                        print("Cancelamento detectado durante espera. Interrompendo.")
                        break
                    time.sleep(1)

                # se refine terminou, atualiza a lista de batches
                try:
                    refined = future_refine.result(timeout=0)
                    if isinstance(refined, list):
                        batches = refined
                except concurrent.futures.TimeoutError:
                    pass

                # coleta métricas se prontas (não bloqueante)
                try:
                    metrics = future_metrics.result(timeout=0)
                except concurrent.futures.TimeoutError:
                    metrics = None

                if cancel_file.exists():
                    break

                i += 1

        # 5. Verifica a acuracia do modelo
        valid_results = self.df_results.dropna(subset=["answers", "predictions"])

        precision = precision_score(valid_results["answers"], valid_results["predictions"], zero_division=0)
        recall = recall_score(valid_results["answers"], valid_results["predictions"], zero_division=0)
        f1 = f1_score(valid_results["answers"], valid_results["predictions"], zero_division=0)

        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1 Score: {f1:.4f}")
            
                

                
            

            

    

def main():
    analyser = Analyser(model_name="qwen/qwen3-32b")
    analyser.analyse()

if __name__ == "__main__":
    main()