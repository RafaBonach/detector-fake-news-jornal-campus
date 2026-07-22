import re
from groq import Groq

from service_streamlit.utils import get_api_key

class GroqClient:
    """Essa classe vai enviar e receber mensagens do groq, tratar erros e configurar paramtros"""
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.api_key = get_api_key()

    def chat_groq(self, messages: list[dict[str, str]] | str, params: dict = None) -> str:
        """Essa função vai enviar mensagens para o groq e receber a resposta"""
        groq_client = Groq(api_key=self.api_key)

        try:
            response = groq_client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                seed=42,
                top_p=params.get("top_p") if params and "top_p" in params else 1, # O top_p deve ser entre 0 e 1, sendo 1 o valor padrão.
                max_completion_tokens=params.get("max_completion_tokens") if params and "max_completion_tokens" in params else 4700 # O max_completion_tokens deve ter no máximo a quantidade de tokens máximo de cada modelo.
            )

            content_response = response.choices[0].message.content.strip()
            return content_response
        except Exception as e:
            print(f"Erro ao enviar mensagem para o Groq: {e}")
            raise e
