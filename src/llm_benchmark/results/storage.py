import re
from pathlib import Path
import pandas as pd
class Store:
    def __init__(self, storage_name: str):
        self.storage_name = storage_name

        # Pegar arquivo de salvamento já existente.
        self.path = self.__search_dataset_path__()
        self.__results_dataframe__ = self.__load_dataset__(self.path) if self.path.exists() else None

    def __search_dataset_path__(self) -> Path | None:
        """Procura o caminho do dataset com base no nome fornecido."""
        base_path = Path(__file__).parent.parent / "results"
        dataset_path = base_path / f"{self.storage_name}.csv"
        
        return dataset_path

    def __load_dataset__(self, dataset_path: Path) -> pd.DataFrame:
        """Carrega o dataset em um DataFrame do pandas."""
        if dataset_path.suffix == ".csv":
            return pd.read_csv(dataset_path)
        elif dataset_path.suffix == ".json":
            return pd.read_json(dataset_path)
        else:
            raise ValueError(f"Formato de arquivo não suportado: {dataset_path.suffix}")
    
    def save_results(self, results: pd.DataFrame):
        """Essa função vai salvar os resultados em um arquivo CSV"""
        # Se self.__results_dataframe__ for None, significa que não há resultados anteriores, então criamos um novo DataFrame.
        if self.__results_dataframe__ is None:
            self.__results_dataframe__ = pd.DataFrame(columns=results.columns)
        
        # Concatenar os resultados existentes com os novos resultados
        self.__results_dataframe__ = pd.concat([self.__results_dataframe__, results], ignore_index=True)
        self.__results_dataframe__.to_csv(self.path, index=False)
        print(f"Resultados salvos em {self.path}")

    '''
    def save_results(self, results: dict[str, float]):
        """Essa função vai salvar os resultados em um arquivo CSV"""

        df = pd.DataFrame.from_dict(results, orient="index", columns=["Previsão", "Resposta"])

        # Se self.__results_dataframe__ for None, significa que não há resultados anteriores, então criamos um novo DataFrame.
        if self.__results_dataframe__ is None:
            self.__results_dataframe__ = pd.DataFrame(columns=df.columns)
        
        # Concatenar os resultados existentes com os novos resultados
        self.__results_dataframe__ = pd.concat([self.__results_dataframe__, df], ignore_index=True)
        self.__results_dataframe__.to_csv(self.path, index=False)
        print(f"Resultados salvos em {self.path}")

    '''
