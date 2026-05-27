"""
Observação: A implementação não está funcionando para mais de um batch.
    - Preciso ajustar um loop que enviar todos os batches para o groq.
    - Caso haja NaN no DataFrame, as linhas com NaN devem ser ignoradas.
"""
import pandas as pd
import json
import itertools
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

# Contantes
REQUESTINTERVAL = 10  # Intervalo entre requisições em segundos
DATABASES_PATH = {
    "fake-br": "pre-processed_tratada.csv",
    "fake-recogna_no_removal_words": "FakeRecogna_no_removal_words_tratada.csv",
    "fake-recogna2": "FakeRecogna_tratada.csv"
}
MAX_RETRIES: 2

class Analyser:
    def __init__(self, model_name, database_name, database_length_limit: int | None = None):
        self.model_name = model_name
        self.api_key = get_api_key("groq_analyser")
        self.base_prompt = [
            {
                "role": "system",
                "content": PROMPTS["base"]["zero-shot"]
            }
        ]
        self.database_name = database_name
        self.database_length_limit = database_length_limit
        self.database = None
        self.df_results = pd.DataFrame()

        self.__set_database__(DATABASES_PATH[self.database_name])

        self.output_dir = Path("artifacts") / "analyser"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_path = self.output_dir / "df_results.csv"
        self.responses_path = self.output_dir / "responses.jsonl"
        self.__wait_time_llm_request__ = time.time()   

    def __set_database__(self, database_path: str):
        """
        Carrega o CSV da base de dados, com tratamento de erros aprimorado para casos comuns como arquivo vazio ou formato inválido.
        Parâmetros:
        - database_path: Caminho para o arquivo CSV da base de dados.
        """
        try:
            resolved_database_path = self._resolve_database_path(database_path)
            self.database = pd.read_csv(resolved_database_path)
            if self.database_length_limit is not None:
                self.database = self.database.head(self.database_length_limit)

        except pd.errors.EmptyDataError as e:
            print(f"Erro ao carregar database de {database_path}: arquivo vazio ou formato inválido. Detalhes: {e}")
            self.database = None

        except Exception as e:
            print(f"Erro inesperado ao carregar database de {database_path}: {e}")
            self.database = None

    def _resolve_database_path(self, database_path: str) -> Path:
        """
        Resolve um caminho absoluto/relativo ou procura o CSV pelo nome dentro do workspace.
        Parâmetros:
        - database_path: Pode ser um caminho absoluto, um caminho relativo ou apenas o nome do arquivo.
        Retorna:
        - Path: O caminho resolvido para o arquivo CSV.
        """
        """Resolve um caminho absoluto/relativo ou procura o CSV pelo nome dentro do workspace."""
        candidate = Path(database_path)

        if candidate.exists():
            return candidate

        search_names = [candidate.name]
        if candidate.suffix.lower() != ".csv":
            search_names.append(f"{candidate.name}.csv")

        search_roots = [Path.cwd(), Path.cwd() / "src", Path.cwd() / "src" / "database"]

        for search_name in search_names:
            for root in search_roots:
                if not root.exists():
                    continue

                exact_matches = sorted(root.rglob(search_name))
                if exact_matches:
                    if len(exact_matches) > 1:
                        print(
                            f"Aviso: mais de um CSV encontrado para '{database_path}'. "
                            f"Usando '{exact_matches[0]}'."
                        )
                    return exact_matches[0]

        raise FileNotFoundError(
            f"Não foi possível localizar o CSV '{database_path}'. "
            "Use um caminho válido ou o nome exato da planilha."
        )

    def prepare_dataframe(self, dataframe: pd.DataFrame, text_column: str) -> pd.DataFrame:
        """Remove linhas sem texto ou sem classe e normaliza o índice para batching."""
        cleaned_dataframe = dataframe.dropna(subset=[text_column, "Classe"]).copy()
        return cleaned_dataframe.reset_index(drop=True)

    def set_df_results(self, prediction: list[int], answer: list[int] | None) -> pd.DataFrame:
        if self.df_results.empty:
            if answer is not None and "answers" not in self.df_results.columns:
                self.df_results["answers"] = pd.Series(answer).astype('Int64').reset_index(drop=True)
            
            # adiciona as respostas da LLM
            self.df_results["predictions"] = pd.Series(prediction).astype('Int64').reset_index(drop=True)
        
        else:
            # incrementa as respostas da LLM ao conjunto de respostas existente
            indices_nulos = self.df_results[self.df_results["predictions"].isna()].index[:len(prediction)]
            self.df_results.loc[indices_nulos, "predictions"] = prediction[:len(indices_nulos)]
        
        return self.df_results

    def save_results(self, df: pd.DataFrame | None = None)-> None:
        if df is not None:
            self.df_results = df
        
        dir_results_path = self.output_dir / f"df_results_{self.database_name}.csv"
        
        # Salva o DataFrame completo com respostas e predições
        self.df_results.to_csv(dir_results_path, index=True)
        print(f"Resultados salvos em: {dir_results_path}")

    def save_metrics(self, metrics: dict[str, float]) -> None:
        metrics_path = self.output_dir / f"metrics_{self.database_name}.json"
        with metrics_path.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
        print(f"Métricas salvas em: {metrics_path}")

    def split_dataframe(
        self,
        dataframe: pd.DataFrame,
        text_column: str,
        max_estimated_tokens: int = 5000,
    ) -> list[pd.DataFrame]:
        dataframe = self.prepare_dataframe(dataframe, text_column)
        batches = []
        current_positions = []
        current_estimated_tokens = 0

        for position, text in enumerate(dataframe[text_column].astype(str).tolist()):
            estimated_tokens = max(1, len(text) // 4) + 40

            if current_positions and current_estimated_tokens + estimated_tokens > max_estimated_tokens:
                batches.append(dataframe.iloc[current_positions].copy())
                current_positions = []
                current_estimated_tokens = 0

            current_positions.append(position)
            current_estimated_tokens += estimated_tokens

        if current_positions:
            batches.append(dataframe.iloc[current_positions].copy())

        return batches

    def build_prompt(self, text_column: str, batch_df: list[pd.DataFrame] | None) -> list[list[dict]]:
        """
        Constrói o prompt para a análise dos dados.
        Inputs:
        - text_column: Nome da coluna do DataFrame que contém o texto da notícia.
        - batch_df (opcionais): DataFrame contendo o batch de notícias a ser analisado.
        """
        batch_prompts = []
        prompt = deepcopy(self.base_prompt)


        if batch_df is None:
            batch_df = [self.database]
        
        for batch in batch_df:
            valid_batch = batch.dropna(subset=[text_column]).copy()
            items = []
            for news_index, news_text in valid_batch[text_column].items():
                if pd.isna(news_text):
                    continue
                items.append({
                    "news_index": int(news_index),
                    "news_text": str(news_text).replace("\n", " ").strip(),
                })

            prompt = deepcopy(self.base_prompt)
            prompt.append({
                "role": "user",
                "content": json.dumps({
                    "batch_size": len(items),
                    "items": items,
                    "expected_classifications": len(items),
                }, ensure_ascii=False)
            })

            batch_prompts.append(prompt)

        return batch_prompts

    def chat_groq(self, messages: list[dict], expected_count: int | None = None) -> list[dict] | None:
        groq_client = Groq(api_key=self.api_key)

        max_tokens = 1024 if expected_count is None else max(256, expected_count * 8)

        response = groq_client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            temperature=0.0,
            seed=42,
            top_p=1,
            max_tokens=max_tokens,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content.strip()
        json_content = None
        try:
            json_content = json.loads(content)
        except json.JSONDecodeError:
            print(f"Erro ao decodificar resposta JSON: {content}")
        return json_content

    def extract_predictions(self, response: dict) -> list[int] | None:
        if not isinstance(response, dict):
            print(f"Resposta inesperada (não é um dict): {response}")
            return None
        
        classifications = response.get("classifications")
        if not isinstance(classifications, list) or not all(isinstance(c, int) for c in classifications):
            print(f"Campo 'classifications' ausente ou inválido na resposta: {response}")
            return None
        
        return classifications

    def compute_metrics(self) -> dict[str, float]:
        """ Observação: Essa função excluir as linhas com NaN para a mensura dos dados.
        Talvez isso deva ser melhor tratado no futuro.
        """
        results = self.df_results.dropna(subset=["predictions"])

        print(results.info())

        precision = precision_score(results["answers"], results["predictions"], zero_division=0)
        recall = recall_score(results["answers"], results["predictions"], zero_division=0)
        f1 = f1_score(results["answers"], results["predictions"], zero_division=0)

        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")

        return {"precision": precision, "recall": recall, "f1": f1}
    
    def timer_check(self, limit=REQUESTINTERVAL):
        elapsed_time = time.time() - self.__wait_time_llm_request__
        if elapsed_time < limit:
            wait_time = limit - elapsed_time
            print(f"Aguardando {wait_time:.2f} segundos para a próxima requisição...")
            time.sleep(wait_time)
        self.__wait_time_llm_request__ = time.time()  # Reinicia o timer
        return True

    def check_prediction(self, list_response: list[int], list_id_prompt: list[int]) -> list[int]:
        """
        Verificador que verifica se o número de predições retornado pela LLM corresponde ao número de
        notícias enviadas no Batch. Caso o número de predições seja menor, retorna os IDs das notícias
        que não receberam predições.
        Entradas:
        - list_response: Lista de dicionários retornada pela LLM
        - list_id_prompt: Lista de IDs das notícias enviadas no prompt
        Saída:
        - missing_ids: Lista de IDs das notícias que não receberam predições ou uma lista vazia.
        """
        missing_ids = []

        if not isinstance(list_response, list):
            print(f"Resposta inesperada (não é uma lista): {list_response}")
            return missing_ids
                
        for id_prompt, pred in itertools.zip_longest(list_id_prompt, list_response, fillvalue=None):
            if pred is None:
                missing_ids.append(id_prompt)

        if len(missing_ids) > 0:
            print(f"Predições faltantes para os IDs: {missing_ids}")
        
        return missing_ids
    
def main():
    #0. Cria um objeto analyser
    analyser = Analyser(model_name="meta-llama/llama-4-scout-17b-16e-instruct", database_name="fake-recogna_no_removal_words", database_length_limit=1000)

    #1. Pegar as notícias que serão analisadas, juntar ao prompt base e enviar para o groq fazer análise.
    # 1.1 Separa as notícias em batches (se necessário) para não estourar limite de tokens do groq
    clean_database = analyser.prepare_dataframe(analyser.database, text_column="Titulo")
    batche_news = analyser.split_dataframe(clean_database, text_column="Titulo", max_estimated_tokens=29000)

    # 1.2 Envia cada batch para o groq e salva as respostas completas
    batch_prompts = analyser.build_prompt(text_column="Titulo", batch_df=batche_news)

    list_answers = clean_database["Classe"].astype(int).tolist()
    """" ______Preciso implementar um loop para enviar cada batch, extrair as predições e incrementar o DataFrame de resultados a cada batch.______ """
    # 2. Envia o lote de prompts um de vada vez através de um loop.
    for i, (batch_prompt, batch_news) in enumerate(zip(batch_prompts, batche_news)):
        if i > 0:
            # Verifica se pode enviar a próxima requisiçao
            analyser.timer_check(limit=REQUESTINTERVAL)
        else:
            analyser.__wait_time_llm_request__ = time.time()  # Inicia o timer para a primeira requisição

        # pending_df: notícias ainda sem predição neste batch
        # pending_predictions: predições já coletadas para este batch (indexadas pelo índice do df)
        pending_df = batch_news.copy()
        collected_predictions: dict[int, int] = {}  # {índice_original: predição}

        attempt = 0

        while (len(pending_df) > 0) and (attempt < MAX_RETRIES):  # Limite de tentativas para evitar loop infinito
            attempt += 1
            print(f"  Tentativa {attempt}/{MAX_RETRIES} — enviando {len(pending_df)} notícias...\n")


            print(f"Enviando batch {i+1}/{len(batch_prompts)} para o Groq...")

            #2.1 Envia um batch de notícias
            #response = analyser.chat_groq(batch_prompt, expected_count=len(pending_df))

            #2.2 Extrair as predições do groq e seta o DataFrame de resultados
            #predictions = analyser.extract_predictions(response)
            """ APENAS PARA TESTE, REMOVER DEPOIS: """
            predictions = [0] * (len(pending_df)-30) 

            if predictions is None:
                print(f"  Tentativa {attempt}: resposta inválida. Tentando novamente...")
                continue

            #2.3 Verifica as predições faltantes
            pending_ids = pending_df.index.tolist()
            missing_ids = analyser.check_prediction(predictions, pending_ids)

            # Mapeia as predições recebidas para os índies originais
            for idx, pred in zip (pending_ids, predictions):
                collected_predictions[idx] = pred
            
            if not missing_ids:
                print(f"  ✓ Todas as {len(pending_df)} predições recebidas.")
                pending_df = pd.DataFrame()  # Zera — batch completo
                break

            # Monta novo sub-batch apenas com as notícias faltantes
            print(f"  {len(missing_ids)} predições faltantes. Remontando sub-batch...")
            pending_df = batch_news.loc[missing_ids].copy()
            current_prompt = analyser.build_prompt(text_column="Titulo", batch_df=[pending_df])[0]
            analyser.timer_check(limit=REQUESTINTERVAL)


        #2.4 Após retires, preenche com NAN os índices que continuaram sem predições
        if len(pending_df) > 0:
            print(
                f"  ✗ Batch {i+1}: {len(pending_df)} notícias sem predição após "
                f"{MAX_RETRIES} tentativas. Preenchendo com NaN."
            )
            for idx in pending_df.index.tolist():
                collected_predictions[idx] = pd.NA

        #2.5 Grava as predições coletadas no df_results na ordem correta
        for idx, pred in collected_predictions.items():
            analyser.df_results.at[idx, "predictions"] = pred

        print(f"  df_results atualizado: {analyser.df_results['predictions'].notna().sum()} predições acumuladas.")
    
    #3 Salva o DataFrame de resultados completo (respostas + predições)
    analyser.save_results()

    #2.3 Calcular métricas de avaliação (precision, recall, f1)
    metrics = analyser.compute_metrics()

    #2.4 Salva as métricas
    analyser.save_metrics(metrics)

if __name__ == "__main__":
    main()