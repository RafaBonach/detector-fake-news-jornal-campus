""" --------------- Ainda falta calcular as métricas ---------------- """
import time
import pandas as pd
from llm_benchmark.datasets.loader import DatasetLoader
from llm_benchmark.datasets.processor import Processor
from llm_benchmark.datasets.splitter import Splitter
from llm_benchmark.prompt.builder import PromptBuilder
from llm_benchmark.llm.groq_client import GroqClient
from llm_benchmark.results.result_handler import ResultHandler
from llm_benchmark.results.storage import Store

PREVISAO_COLUMN = "Classe"

def token_counter(prompt: list[dict[str, str]]) -> int:
    """Conta a quantidade de tokens aproximada um texto possui"""
    text = " ".join([msg["content"] for msg in prompt])
    estimated_tokens = max(1, len(text) // 4) + 879

    return estimated_tokens

def benchmark():
    """Função principal para executar o benchmark de LLMs."""
    # 0. Parametros de configuração
    params = {
        "model_name": "meta-llama/llama-4-scout-17b-16e-instruct",
        "base_prompt_name": "zero-shot",
        "bool_def": False,
        "df_text_column": "Titulo",
        "database_name": "FakeRecogna_1.csv",
        "top_p": 1,
        "max_completion_tokens": 8192
    }

    #1. Carrega dataset
    df = DatasetLoader(params["database_name"])

    df_processed = Processor(df.get_dataframe(), params["df_text_column"], PREVISAO_COLUMN)
    df_processed = df_processed.extract()

    #2. Converte o dataframe em prompt.
    print(f"Processando o dataframe com {len(df_processed)} linhas.\n")
    prompt_builder = PromptBuilder(params["base_prompt_name"], params["bool_def"])
    
    prompt_builder.add_prompts(df_processed[params["df_text_column"]].tolist())

    prompt = prompt_builder.get_prompt()

    #2.1. Verifica se o prompt excede o limite de tokens estimado
    estimated_tokens = token_counter(prompt)
    print(f"Prompt estimado em {estimated_tokens} tokens.")
    
    '''
    if estimated_tokens > params["max_completion_tokens"]:
        raise ValueError(f"O prompt excede o limite de tokens estimado: {estimated_tokens} > {params['max_completion_tokens']}.")
    '''
    #3. Envia o prompt para o modelo
    groq_client = GroqClient(params["model_name"])
    response = groq_client.chat_groq(prompt, params)

    print(f"Resposta do modelo: {response}")
    
    #4. Tratar a resposta do modelo
    result_handler = ResultHandler()
    if not isinstance(response, Exception):
        prevision = {index: row[PREVISAO_COLUMN] for index, row in df_processed.iterrows()}
        results = result_handler.process_results(prevision, response)
        print(f"Resultados do chunk: {results.head()}")

        #5. Salvar resultados em um arquivo CSV
        storage = Store(f"{params['database_name'].replace('.csv', '')}_results")
        storage.save_results(results)

        #6. Calcular as métricas
        """ --------------- Ainda falta calcular as métricas ---------------- """

    return "Benchmark executado com sucesso!"

if __name__ == "__main__":
    print(benchmark())