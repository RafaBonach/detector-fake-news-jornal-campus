"""
Analyzer para classificação de notícias usando modelos LLM via Groq.
- Processa múltiplos batches de notícias
- Preenche com NaN as predições faltantes (sem retry)
- Calcula métricas de avaliação (precision, recall, f1)
"""
import re
import pandas as pd
import json
import itertools
from copy import deepcopy
from pathlib import Path
from dotenv import load_dotenv
import time

from sklearn.metrics import precision_score, recall_score, f1_score # Métricas de avaliação

from config_base import PROMPTS
from service_streamlit.utils import get_api_key

from groq import Groq

# --- Setup ---
load_dotenv()

# Contantes
REQUESTINTERVAL = 10  # Intervalo entre requisições em segundos
JSON_VALIDATE_RETRY_WAIT = 60  # Espera antes de tentar novamente em caso de JSON inválido
SHORT_DF_NAME = {
    "pre-processed_tratada.csv": "FB",
    "FakeRecogna_no_removal_words_tratada.csv": "FR1",
    "FakeRecogna_tratada.csv": "FR2"
}
DATABASES_PATH = {
    "fake-br": "pre-processed_tratada.csv",
    "fake-recogna_no_removal_words": "FakeRecogna_no_removal_words_tratada.csv",
    "fake-recogna2": "FakeRecogna_tratada.csv"
}


class Analyser:
    def __init__(self, model_name: str, base_prompt_name: str, bool_def: bool, database_name: str, database_length_limit: int | None = None):
        # Configurações do modelo
        self.model_name = model_name
        self.api_key = get_api_key("groq_analyser")

        # Configurações do prompt
        self.base_prompt = None
        self.__set_base_prompt__(key_base=base_prompt_name, bool_def=bool_def)

        # Configurações da base de dados
        self.database_name = database_name
        self.database_length_limit = database_length_limit
        self.database = None
        self.df_results = pd.DataFrame()
        self.__set_database__(self.database_name)

        # Configurações de saída — usar a pasta `src/artifacts/analyser`
        self.output_dir = Path(__file__).resolve().parent.parent / "artifacts" / "analyser"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.results_path = self.output_dir / "df_results.csv"
        self.responses_path = self.output_dir / "responses.jsonl"

        # Outras configurações
        self.__wait_time_llm_request__ = time.time()

    def __set_base_prompt__(self, key_base: str = "zero-shot", bool_def: bool = False):
        """Configura o prompt base a ser usado na análise, com base em uma chave pré-definida.
        Parâmetros:
        - key_base: Chave do prompt base a ser usado (deve estar presente em PROMPTS['base'])
        - bool_def: Se True, adiciona a definição de fake news ao prompt base
        """
        if key_base not in PROMPTS["base"]:
            raise ValueError(f"Chave '{key_base}' não encontrada em PROMPTS['base']. Opções disponíveis: {list(PROMPTS['base'].keys())}")
        
        self.base_prompt = [
            {
                "role": "system",
                "content": PROMPTS["base"][key_base]
            }
        ]

        if bool_def:
            self.base_prompt[0]["content"] += f"\n\n{PROMPTS['definition']}"

        """
        if self.model_name.startswith("openai/"):
            self.base_prompt[0]["content"] += no_think
        """

    def __set_database__(self, database_path: str):
        """
        Carrega o CSV da base de dados, com tratamento de erros aprimorado para casos comuns como arquivo vazio ou formato inválido.
        Parâmetros:
        - database_path: Caminho para o arquivo CSV da base de dados.
        """
        try:
            resolved_database_path = self._resolve_database_path(database_path)
            self.database = pd.read_csv(resolved_database_path)
            if self.database_length_limit is not None and len(self.database) > self.database_length_limit:
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

    def set_answers(self, dataframe: pd.DataFrame, answer_column: str = "Classe") -> None:
        """
        Salva as respostas esperadas da coluna especificada do dataframe em df_results.
        Parâmetros:
        - dataframe: DataFrame contendo a coluna com as respostas esperadas
        - answer_column: Nome da coluna que contém as respostas (padrão: "Classe")
        """
        if answer_column not in dataframe.columns:
            raise ValueError(f"Coluna '{answer_column}' não encontrada no DataFrame.")
        
        answers = dataframe[answer_column].astype('Int64').reset_index(drop=True)
        self.df_results["answers"] = answers
        print(f"✓ {len(answers)} respostas carregadas em df_results['answers']")

    def set_predictions(self, idx: int, prediction: int | float) -> None:
        """
        Define uma predição específica no df_results na posição fornecida.
        Parâmetros:
        - idx: Índice da linha no df_results
        - prediction: Valor da predição ou NaN
        """
        self.df_results.at[idx, "predictions"] = prediction

    def save_results(self, df: pd.DataFrame | None = None)-> None:
        if df is not None:
            self.df_results = df

        print(self.model_name)

        results_name = re.match(r"[a-zA-Z]+", self.model_name).group()
        results_name += f"_{SHORT_DF_NAME.get(self.database_name, self.database_name)}"
        
        dir_results_path = self.output_dir / f"{results_name}.csv"
        
        # Salva o DataFrame completo com respostas e predições
        self.df_results.to_csv(dir_results_path, index=True)
        print(f"    ✓ Resultados salvos em: {dir_results_path}")

    def save_metrics(self, metrics: dict[str, float]) -> None:
        metrics_name = "metrics_"
        metrics_name += re.match(r"[a-zA-Z]+", self.model_name).group()
        metrics_name += f"_{SHORT_DF_NAME.get(self.database_name, self.database_name)}"
        metrics_path = self.output_dir / f"{metrics_name}.json"
        with metrics_path.open("w", encoding="utf-8") as fh:
            fh.write(json.dumps(metrics, ensure_ascii=False, indent=2) + "\n")
        print(f"    ✓ Métricas salvas em: {metrics_path}")

    def split_dataframe(
        self,
        dataframe: pd.DataFrame,
        text_column: str,
        max_estimated_tokens: int = 10000,
    ) -> list[pd.DataFrame]:
        #dataframe = self.prepare_dataframe(dataframe, text_column)
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

        #--------------------DEBUG: Verificando o prompt enviado ao Groq
        #print(f"\n\n\nMensagem enviada ao Groq:\n{messages}\n\n\n")

        MAX_RETRIES = 2
        count_400 = 0

        attempt = 0
        while True:
            attempt += 1
            try:
                response = groq_client.chat.completions.create(
                    messages=messages,
                    model=self.model_name,
                    temperature=0.2,
                    seed=42,
                    top_p=1,
                    # O max_completion_tokens deve ter no máximo a quantidade de tokens máximo de cada modelo.
                    max_completion_tokens=8000,
                    #response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content.strip()
                
                #DEBUG: Verificando saída
                print(f"\n\n\nResposta bruta do Groq:\n{content}\n\n\n")
                try:
                    return json.loads(content)
                except json.JSONDecodeError:
                    print(f"\nErro ao decodificar resposta JSON: {content}\n")
                    return None
            
            except Exception as exc:
                status_code = getattr(exc, "status_code", None)
                error_message = str(exc)

                #-- 400: json_validate_failed --
                if status_code == 400 and "json_validate_failed" in error_message:
                    count_400 += 1
                    if count_400 < MAX_RETRIES:
                        print(f"Erro 400 (tentativa {count_400}/{MAX_RETRIES}). "
                          f"Aguardando 60s antes de tentar novamente...")
                        time.sleep(60)
                        continue
                    print(f"\nErro 400 persistente após {MAX_RETRIES} tentativas. Abortando.\n")
                    raise

                #-- 429: rate_limit -- Lê o tempo de espera da mensagem --
                elif status_code == 429 or "rate_limit" in error_message.lower() or "429" in error_message:
                    wait_time = 60  # Valor padrão
                    match = re.search(r"Please try again in \s+(\d+)\s*s", error_message, re.IGNORECASE)
                    if match:
                        wait_time = float(match.group(1))
                    print(f"\nErro 429 (rate limit). Aguardando {wait_time}s antes de tentar novamente...\n")
                    time.sleep(wait_time)
                    continue

                #-- Outros erros --
                else:
                    raise


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
        """ Calcula métricas de avaliação (precision, recall, f1) excluindo linhas com NaN em predictions. """
        results = self.df_results.dropna(subset=["predictions"]).copy()
        
        if len(results) == 0:
            print(" ⚠ Nenhuma predição válida para calcular métricas.")
            return {"   precision": 0.0, "recall": 0.0, "f1": 0.0}
        
        # Converte para int puro para compatibilidade com sklearn
        y_true = results["answers"].astype(int).values
        y_pred = results["predictions"].astype(int).values
        
        print(f"    Calculando métricas com {len(results)} amostras...")

        precision = precision_score(y_true, y_pred, zero_division=0)
        recall = recall_score(y_true, y_pred, zero_division=0)
        f1 = f1_score(y_true, y_pred, zero_division=0)

        print(f"    Precision: {precision:.4f}")
        print(f"    Recall: {recall:.4f}")
        print(f"    F1-Score: {f1:.4f}")

        return {"precision": precision, "recall": recall, "f1": f1}
    
    def timer_check(self, limit=REQUESTINTERVAL):
        elapsed_time = time.time() - self.__wait_time_llm_request__
        if elapsed_time < limit:
            wait_time = limit - elapsed_time
            print(f"\nAguardando {wait_time:.2f} segundos para a próxima requisição...")
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
    
def main_analyser(model_name: str, base_prompt_name: str, bool_def: bool, df_text_column: str, database_name: str, database_length_limit: int | None = None, max_estimated_tokens: int = 17000):
    """Fluxo principal do analisador
    Parâmetros:
- model_name: Nome do modelo LLM a ser usado para análise (deve estar presente em MODELS)
- base_prompt_name: Nome do prompt base a ser usado presente em config_base
- bool_def: Se True, adiciona a definição de fake news ao prompt base
- df_text_column: Nome da coluna do DataFrame que contém o texto da notícia a ser analisada
- database_name: Nome da base de dados a ser usada (deve estar presente em DATABASES_PATH)
- database_length_limit: Limite opcional para o número de linhas da base de dados a ser processada (útil para testes)
- max_estimated_tokens: Limite máximo de tokens estimados por batch para controle de tamanho do prompt enviado ao modelo
    """
    #0. Cria um objeto analyser
    analyser = Analyser(model_name=model_name, base_prompt_name=base_prompt_name, bool_def=bool_def, database_name=database_name, database_length_limit=database_length_limit)


    print("1. Preparando os dados")
    #1. Pegar as notícias que serão analisadas, juntar ao prompt base e enviar para o groq fazer análise.
    # 1.1 Separa as notícias em batches (se necessário) para não estourar limite de tokens do groq
    clean_database = analyser.prepare_dataframe(analyser.database, text_column=df_text_column)
    batch_news = analyser.split_dataframe(clean_database, text_column=df_text_column, max_estimated_tokens=max_estimated_tokens)


    # 1.2 Envia cada batch para o groq e salva as respostas completas
    batch_prompts = analyser.build_prompt(text_column=df_text_column, batch_df=batch_news)


    # 1.3 Inicializa df_results com as respostas esperadas (answers) usando o método
    analyser.set_answers(clean_database, answer_column="Classe")
    analyser.df_results["predictions"] = pd.NA
    # Checkpoint: Dados preparados com sucesso.
    print(f"    ✓ {len(batch_news)} batches preparados para análise (máx. {max_estimated_tokens} tokens estimados por batch).")


    print("\n2. Enviando batches para análise")
    # 2. Envia o lote de prompts um de cada vez através de um loop.
    for i, (batch_prompt, batch_news) in enumerate(zip(batch_prompts, batch_news)):
        collected_predictions: dict[int, int] = {}  # {índice_original: predição}

        print(f"Enviando batch {i+1}/{len(batch_prompts)} para o Groq...")

        try:
            #2.1 Envia um batch de notícias
            response = analyser.chat_groq(batch_prompt, expected_count=len(batch_news))

            #2.2 Extrair as predições do groq
            predictions = analyser.extract_predictions(response)
        
        # Se a predição der erro, ele preenche as predições com None.
        except Exception as exc:
            print(f"  ✗ Erro ao processar batch {i+1}: {exc}")
            predictions = None

        if predictions is None:
            print(f"  ✗ Resposta inválida para batch {i+1}. Preenchendo com NaN.")
            # Preencher todas as notícias com NaN
            for idx in batch_news.index.tolist():
                collected_predictions[idx] = pd.NA
        else:
            #2.3 Verifica as predições faltantes
            batch_ids = batch_news.index.tolist()
            missing_ids = analyser.check_prediction(predictions, batch_ids)

            # Mapeia as predições recebidas para os índices originais
            for idx, pred in zip(batch_ids, predictions):
                collected_predictions[idx] = pred
            
            # Preenche com NaN as notícias que não receberam predição
            if missing_ids:
                print(f"  {len(missing_ids)} predições faltantes. Preenchendo com NaN.")
                for idx in missing_ids:
                    collected_predictions[idx] = pd.NA
            else:
                print(f"  ✓ Todas as {len(batch_news)} predições recebidas.")

        #2.4 Grava as predições coletadas no df_results na ordem correta usando o método
        for idx, pred in collected_predictions.items():
            analyser.set_predictions(idx, pred)

        print(f"  Batch {i+1} concluído: {analyser.df_results['predictions'].notna().sum()} predições acumuladas (com NaN).")
    #checkpoint: Batches processados com sucesso.
    print(" ✓ Todos os batches processados.")


    print("\n3. Salvando resultados ")
    #3 Salva o DataFrame de resultados completo (respostas + predições)
    analyser.save_results()
    

    print("\n4. Calculando métricas de avaliação")
    #4.1 Calcular métricas de avaliação (precision, recall, f1)
    metrics = analyser.compute_metrics()

    #4.2 Salva as métricas
    analyser.save_metrics(metrics)
    print('\n✓ Análise concluída!\n')

def main():
    print("\n----- ANALISE: openai/gpt-oss-120b -----\n")
    main_analyser(
        model_name="meta-llama/llama-4-scout-17b-16e-instruct",
        base_prompt_name="zero-shot",
        bool_def=False,
        df_text_column="Titulo",
        database_name=DATABASES_PATH["fake-recogna2"],
        database_length_limit=1000,
        max_estimated_tokens=10000
    )
    print("----- FIM DA ANALISE -----\n")


if __name__ == "__main__":
    main()