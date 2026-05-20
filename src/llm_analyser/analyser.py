"""
Observação: A implementação não está funcionando para mais de um batch.
    - Preciso ajustar um loop que enviar todos os batches para o groq.
    - Caso haja NaN no DataFrame, as linhas com NaN devem ser ignoradas.
"""
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

# Contantes
REQUESTINTERVAL = 60  # Intervalo entre requisições em segundos
DATABASES_PATH = {
    "fake-br": "/home/rafael/Projetos/campus_multiplataforma_llm/src/database/Fake-Br/pre-processed_tratada.csv",
    "fake-recogna_no_removal_words": "/home/rafael/Projetos/campus_multiplataforma_llm/src/database/FakeRecogna/FakeRecogna_no_removal_words_tratada.csv",
    "fake-recogna2": "/home/rafael/Projetos/campus_multiplataforma_llm/src/database/FakeRecogna/FakeRecogna_tratada.csv"
}

class Analyser:
    def __init__(self, model_name, database_name, database_length_limit=int|None):
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
        self.__wait_time_llm_request__ = None      

    def __set_database__(self, database_path: str):
        try:
            self.database = pd.read_csv(database_path)
            if self.database_length_limit is not None:
                self.database = self.database.head(self.database_length_limit)

        except pd.errors.EmptyDataError as e:
            print(f"Erro ao carregar database de {database_path}: arquivo vazio ou formato inválido. Detalhes: {e}")
            self.database = None

        except Exception as e:
            print(f"Erro inesperado ao carregar database de {database_path}: {e}")
            self.database = None


    def save_results(self, llm_answer: list[int] | None)-> None:
        self.df_results["answers"] = self.database["Classe"].astype(int).to_frame().join(self.df_results)

        if llm_answer is not None:
            self.df_results["predictions"] = pd.Series(llm_answer)


        # Salva o DataFrame completo com respostas e predições
        self.df_results.to_csv(self.output_dir / f"results_{self.database_name}.csv", index=True)
        print(f"Resultados salvos em: {self.output_dir / f'results_{self.database_name}.csv'}")

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
            prompt = deepcopy(self.base_prompt)
            for news_index, news_text in batch[text_column].items():
                news_text = news_text.replace("\n", " ").strip()
                prompt.append({
                    "role": "user",
                    "content": json.dumps({
                        "news_index": int(news_index),
                        "news_text": news_text,
                    }, ensure_ascii=False)
                })

            batch_prompts.append(prompt)

        return batch_prompts

    def chat_groq(self, messages: list[dict]) -> list[dict] | None:
        groq_client = Groq(api_key=self.api_key)

        response = groq_client.chat.completions.create(
            messages=messages,
            model=self.model_name,
            temperature=0.0,
            seed=42,
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

        precision = precision_score(results["answers"], results["predictions"], zero_division=0)
        recall = recall_score(results["answers"], results["predictions"], zero_division=0)
        f1 = f1_score(results["answers"], results["predictions"], zero_division=0)

        print(f"Precision: {precision:.4f}")
        print(f"Recall: {recall:.4f}")
        print(f"F1-Score: {f1:.4f}")

        return {"precision": precision, "recall": recall, "f1": f1}

def main():
    #0. Cria um objeto analyser
    analyser = Analyser(model_name="meta-llama/llama-4-scout-17b-16e-instruct", database_name="fake-recogna_no_removal_words", database_length_limit=100)



    #1. Pegar as notícias que serão analisadas, juntar ao prompt base e enviar para o groq fazer análise.
    # 1.1 Separa as notícias em batches (se necessário) para não estourar limite de tokens do groq
    batche_news = analyser.split_dataframe(analyser.database, text_column="Titulo", max_estimated_tokens=5000)

    # 1.2 Envia cada batch para o groq e salva as respostas completas
    batch_prompts = analyser.build_prompt(text_column="Titulo", batch_df=batche_news)



    """" ______Preciso implementar um loop para enviar cada batch, extrair as predições e incrementar o DataFrame de resultados a cada batch.______ """


    response = analyser.chat_groq(batch_prompts[0]) # Para teste, envia apenas o primeiro batch

    #2. Extrair as predições do groq e salvar
    predictions = analyser.extract_predictions(response)
    print(f"{len(predictions)} predições extraídas: {predictions}")
    analyser.save_results(predictions)
    
    #3.1 Calcular métricas de avaliação (precision, recall, f1)
    metrics = analyser.compute_metrics()

    #3.2 Salva as métricas
    analyser.save_metrics(metrics)



    #analyser.analyse(database_name="fake-br", text_column="preprocessed_news", df_line_limit=1000)
    #analyser.analyse(database_name="fake-recogna1", text_column="Titulo", df_line_limit=1000)
    #analyser.analyse(database_name="fake-recogna2", text_column="Titulo", df_line_limit=1000)

if __name__ == "__main__":
    main()