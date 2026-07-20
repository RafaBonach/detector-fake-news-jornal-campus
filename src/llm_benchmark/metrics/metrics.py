from sklearn.metrics import precision_score, recall_score, f1_score # Métricas de avaliação
import pandas as pd
class Metrics:
    def __init__(self, results: pd.DataFrame):
        self.results = results

    def calculate_precision(self):
        """Calcula a precisão do modelo."""
        return precision_score(self.results['Resposta'].values, self.results['Previsao'].values)

    def calculate_recall(self):
        """Calcula o recall do modelo."""
        return recall_score(self.results['Resposta'].values, self.results['Previsao'].values)

    def calculate_f1_score(self):
        """Calcula o F1-score do modelo."""
        return f1_score(self.results['Resposta'].values, self.results['Previsao'].values)