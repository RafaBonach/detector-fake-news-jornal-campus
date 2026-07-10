import pandas as pd
import re
class ResultHandler:
    def process_results(self, prevision: dict[int, int], llm_answer: str) -> pd.DataFrame:
        """Essa função vai processar os resultados do modelo
        para indice do dataframe, retorna uma tupla com (previsão, resposta)"""
        # Extrai os números da resposta do modelo
        llm_answer_numbers = re.findall(r"\b[01]\b", llm_answer)

        # Cria um dicionário para armazenar os resultados
        results = {}

        # Itera sobre as previsões e respostas do modelo
        for index, prediction in prevision.items():
            # Verifica se o índice está dentro do intervalo da resposta do modelo
            if index < len(llm_answer_numbers):
                llm_response = llm_answer_numbers[index]
                results[index] = (prediction, llm_response)
            else:
                results[index] = (prediction, None)  # Caso não haja resposta do modelo

        return pd.DataFrame.from_dict(results, orient="index", columns=["Previsão", "Resposta"])
    
if __name__ == "__main__":
    # Exemplo de uso da classe ResultHandler
    prevision_example = {0: 1, 1: 0, 2: 1, 3: 0, 4: 1, 5: 0, 6: 1, 7: 0, 8: 1, 9: 0, 10: 1, 11: 0, 12: 1, 13: 0, 14: 1, 15: 0, 16: 1, 17: 0, 18: 1, 19: 0, 20: 1, 21: 0, 22: 1, 23: 0, 24: 1, 25: 0, 26: 1, 27: 0, 28: 1, 29: 0, 30: 1, 31: 0, 32: 1, 33: 0, 34: 1, 35: 0, 36: 1, 37: 0, 38: 1, 39: 0, 40: 1}
    llm_answer_example = '{"classifications": [0, 1, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1'

    result_handler = ResultHandler()
    results_df = result_handler.process_results(prevision_example, llm_answer_example)
    print(results_df)