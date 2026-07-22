"""Responsável por carregar os datasets do benchmark de LLMs."""
from pathlib import Path
import pandas as pd
class DatasetLoader:
    """Classe responsável por carregar os datasets do benchmark de LLMs."""
    
    def __init__(self, dataset_name: str):
        self.dataset_name = dataset_name
        self.dataset_path = self.search_dataset_path()
        self.dataframe = self.load_dataset(self.dataset_path)

    def get_dataframe(self) -> pd.DataFrame:
        """Retorna o DataFrame carregado."""
        return self.dataframe

    def search_dataset_path(self) -> Path:
        """Procura o caminho do dataset com base no nome fornecido."""
        base_path = Path(__file__).parent.parent / "datasets"
        dataset_path = base_path / self.dataset_name

        if not dataset_path.exists():
            raise FileNotFoundError(f"Dataset '{self.dataset_name}' não encontrado em {base_path}")

        return dataset_path
    
    def load_dataset(self, dataset_path: Path) -> pd.DataFrame:
        """Carrega o dataset em um DataFrame do pandas."""
        if dataset_path.suffix == ".csv":
            return pd.read_csv(dataset_path)
        elif dataset_path.suffix == ".json":
            return pd.read_json(dataset_path)
        else:
            raise ValueError(f"Formato de arquivo não suportado: {dataset_path.suffix}")
        