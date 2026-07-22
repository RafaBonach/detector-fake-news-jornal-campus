import pandas as pd
class Processor:
    """Classe responsável por processar os datasets do benchmark de LLMs."""
    
    def __init__(self, dataframe: pd.DataFrame, text_column: str, check_column: str = None):
        self.text_column = text_column
        self.check_column = check_column
        self.dataframe = dataframe

    def extract(self) -> pd.DataFrame:
        """Extrai o texto e a coluna de verificação (se fornecida) do DataFrame."""
        try:
            if self.check_column is not None:
                return self.dataframe[[self.text_column, self.check_column]]
            return self.dataframe[[self.text_column]]
        except KeyError as e:
            raise KeyError(f"Coluna não encontrada no DataFrame: {e}")

    
        