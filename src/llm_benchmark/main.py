""" --------------- Ainda falta calcular as métricas ---------------- """
import re
import time
import pandas as pd
from llm_benchmark.datasets.loader import DatasetLoader
from llm_benchmark.datasets.processor import Processor
from llm_benchmark.prompt.builder import PromptBuilder
from llm_benchmark.llm.groq_client import GroqClient
from llm_benchmark.results.result_handler import ResultHandler
from llm_benchmark.results.handler import Store
from llm_benchmark.metrics.metrics import Metrics

PREVISAO_COLUMN = "Classe"

START_INDEX =57

def __exception_handler__(exception: Exception) -> float | Exception:
        """Essa função vai tratar os erros do groq
        - 429 (rate_limit): retorna o tempo de espera
        - 400 (json_validate_failed): retorna 60 segundos como tempo de espera
        - outros erros: retorna a mensagem de erro"""
        
        status_code = getattr(exception, "status_code", None)
        error_message = str(exception).lower()

        wait_time = float(60)

        if status_code == 429 or "rate limit" in error_message or "429" in error_message:
            print(f"Erro 429: {exception}. Aguardando {wait_time} segundos antes de tentar novamente...")
            match = re.search(r"please try again in \s+(\d+)\s*s", error_message, re.IGNORECASE)
            if match:
                wait_time = float(match.group(1))
                return wait_time
            else:
                return wait_time
            
        elif status_code == 400 and "json_validate_failed" in error_message:
            print(f"Erro 400: {error_message}. Aguardando {wait_time} segundos antes de tentar novamente...")
            return wait_time
        
        print(f"Erro inesperado: {error_message}.")
        raise exception

def __save_metrics__(metrics: tuple[float, float, float], dataset_name: str) -> None:
    """Salva as métricas em um arquivo CSV"""
    df_metrics = pd.DataFrame([{
        "precision": metrics[0],
        "recall": metrics[1],
        "f1_score": metrics[2]
    }])
    
    df_metrics.to_csv(f"{dataset_name}_metrics.csv", index=False)
    print(f"Métricas salvas em {dataset_name}_metrics.csv")

def token_counter(prompt: list[dict[str, str]]) -> int:
    """Conta a quantidade de tokens aproximada um texto possui"""
    text = " ".join([msg["content"] for msg in prompt])
    estimated_tokens = max(1, len(text) // 4) + 879

    return estimated_tokens

def benchmark(params: dict = None) -> str:
    """Função principal para executar o benchmark de LLMs."""
    # 0. Verifica existência de parâmetros obrigatórios
    if {"model_name", "base_prompt_name", "df_text_column", "database_name", "top_p", "max_completion_tokens"} != params.keys():
        raise ValueError("Parâmetros insuficientes fornecidos. Certifique-se de incluir 'model_name', 'base_prompt_name', 'df_text_column', 'database_name', 'top_p' e 'max_completion_tokens'.")
    

    #1. Carrega dataset
    df = DatasetLoader(params["database_name"])

    df_processed = Processor(df.get_dataframe(), params["df_text_column"], PREVISAO_COLUMN)
    df_processed = df_processed.extract()

    for ind in range(START_INDEX, len(df_processed)):

        prompt = df_processed.iloc[ind][params["df_text_column"]]

        print(f"\n\nExecução numero {ind + 1}/{len(df_processed)}\n")
        #2. Converte o dataframe em prompt.
        print(f"Processando o dataframe com {len(df_processed)} linhas.\n")
        prompt_builder = PromptBuilder(params["base_prompt_name"])


        # debug
        print(f"Pegunta:\n{prompt}\n\n")


        prompt_builder.add_prompts([prompt])

        prompt = prompt_builder.get_prompt()

        '''
        #2.1. Verifica se o prompt excede o limite de tokens estimado
        estimated_tokens = token_counter(prompt)
        print(f"Prompt estimado em {estimated_tokens} tokens.")
        
        
        if estimated_tokens > params["max_completion_tokens"]:
            raise ValueError(f"O prompt excede o limite de tokens estimado: {estimated_tokens} > {params['max_completion_tokens']}.")
        '''

        # debug
        #print(f"\n\nPrompt enviado para o modelo:\n{prompt}\n\n")

        #3. Envia o prompt para o modelo
        groq_client = GroqClient(params["model_name"])
        response = groq_client.chat_groq(prompt, params)

        # Debug
        print(f"Resposta do modelo:\n{response}\n\n")
        
        
        #4. Tratar a resposta do modelo
        result_handler = ResultHandler()
        if not isinstance(response, Exception):
            prevision = df_processed.loc[ind, PREVISAO_COLUMN]
            results = result_handler.process_results(ind, prevision, response)

            if results is None:
                raise ValueError("A LLM não deu um resultado ou não possui previsão para o resultado retornado, resposta Nula.")

            #5. Salvar resultados em um arquivo CSV
            storage = Store(f"{params['database_name'].rsplit('_', 1)[0]}_results")
            storage.save_results(results)
        else:
            raise response

def metrics(dataset_name: str = None):
    """Função para calcular métricas de avaliação do modelo."""

    # Implementar cálculo de métricas como acurácia, precisão, recall, F1-score, etc.
    if dataset_name is None:
        raise ValueError("Nome do dataset não fornecido para cálculo de métricas.")
    
    store = Store(dataset_name)
    df_results = store.get_results()

    if df_results is None:
        raise ValueError(f"Não há resultados armazenados para o dataset '{dataset_name}'.")

    # Verifica o tipo das colunas e converte para float se necessário
    if df_results["Resposta"].dtype != float:
        df_results["Resposta"] = pd.to_numeric(df_results["Resposta"], errors='coerce')
    if df_results["Previsao"].dtype != float:
        df_results["Previsao"] = pd.to_numeric(df_results["Previsao"], errors='coerce')

    # Remove as linhas que tiverem nan
    df_results = df_results.dropna(subset=["Resposta", "Previsao"])

    '''
    (y_true, y_pred) = (df_results["Resposta"].values, df_results["Previsao"].values)
    print(f"Resultados carregados para cálculo de métricas:\n{y_true}\n{y_pred}")
    '''
    metrics = Metrics(df_results)

    results = [metrics.calculate_precision(), metrics.calculate_recall(), metrics.calculate_f1_score()]

    # Calculo da precisão:
    print(f"Precisão: {results[0]}")
    # Calculo do recall:
    print(f"Recall: {results[1]}")
    # Calculo do F1-score:
    print(f"F1-score: {results[2]}")

    __save_metrics__(results, dataset_name)

    

if __name__ == "__main__":
    """
    * Zero-shot - fakerecogna - meta-llama concluido.

    """
    params = {
        "model_name": "qwen/qwen3.6-27b",
        "base_prompt_name": "few-shot",
        "df_text_column": "Noticia",
        "top_p": 1,
        "max_completion_tokens": 4000
    }
    
    params["database_name"] = "amostra_FakeRecogna_anomaly.csv"

    benchmark(params)
    '''
    for i in range(1, 10):
        params["database_name"] = f"FakeRecogna_{i}.csv"

        #debug
        print(f"Processando o chunk {i} com o arquivo {params['database_name']}...\n")
        
        max_attempts = 2

        for attempt in range(max_attempts):
            try:
                bm_result = benchmark(params)

                # debug
                print(f"Chunk {i} processado com sucesso na tentativa {attempt + 1}.\n")
                time.sleep(1)  # Pequena pausa antes de processar o próximo chunk

                break
            except Exception as e:
                
                #debug
                print(f"Erro ao processar o chunk {i} na tentativa {attempt + 1}: {e}\n")


                wait_time = __exception_handler__(e)

                
                if not isinstance(wait_time, float):
                    break

                if attempt < max_attempts - 1:
                    print(f"Aguardando {wait_time} segundos antes de tentar novamente...")
                    time.sleep(wait_time)
            
        else:
            print("Todas as tentativas falharam.")
            break

    print(f"Benchmark concluído com sucesso! {i} chunks processados.\n")
    '''
    
    # Calcular as métricas
    """ --------------- Ainda falta calcular as métricas ---------------- """
    metrics("amostra_FakeRecogna_results")