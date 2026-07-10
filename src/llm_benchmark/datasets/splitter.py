import pandas as pd

class Splitter:
    """Responsável por dividir o dataframe em partes menores."""
    def __init__(self, dataframe: pd.DataFrame, max_estimated_tokens: int):
        self.dataframe = dataframe
        self.max_estimated_tokens = max_estimated_tokens
        self.chunks = []

    def split(self, text_column: str) -> list[pd.DataFrame]:
        """Baseado no máximo de tokens, ele irá verificar quantos tokens cada linha possui.
        Quando atingir o valor máximo, ele corta o dataframe e cria um novo chunk."""
        chunks = []
        current_chunk = pd.DataFrame()
        current_estimated_tokens = 0


        for i , row in self.dataframe.iterrows():
            text = row[text_column]
            estimated_tokens = self.token_counter(text)

            if current_estimated_tokens + estimated_tokens <= self.max_estimated_tokens:
                current_chunk = pd.concat([current_chunk, pd.DataFrame([row], index=[i])], ignore_index=True)
                current_estimated_tokens += estimated_tokens
            else:
                chunks.append(current_chunk)
                current_chunk = pd.DataFrame([row], index=[i])
                current_estimated_tokens = estimated_tokens

        if not current_chunk.empty:
            chunks.append(current_chunk)

        self.chunks = chunks

        return chunks

    def token_counter(self, text: str) -> int:
        """Conta a quantidade de tokens aproximada um texto possui"""
        estimated_tokens = max(1, len(text) // 4) + 40

        return estimated_tokens
