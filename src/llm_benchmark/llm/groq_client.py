import re
from groq import Groq

from service_streamlit.utils import get_api_key

class GroqClient:
    """Essa classe vai enviar e receber mensagens do groq, tratar erros e configurar paramtros"""
    def __init__(self, model_name: str):
        self.model_name = model_name
        self.api_key = get_api_key()

    def chat_groq(self, messages: list[dict[str, str]], params: dict = None) -> str | Exception:
        """Essa função vai enviar mensagens para o groq e receber a resposta"""
        groq_client = Groq(api_key=self.api_key)

        try:
            response = groq_client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                seed=42,
                top_p=params.get("top_p") if params and "top_p" in params else 1, # O top_p deve ser entre 0 e 1, sendo 1 o valor padrão.
                max_completion_tokens=params.get("max_completion_tokens") if params and "max_completion_tokens" in params else 4096 # O max_completion_tokens deve ter no máximo a quantidade de tokens máximo de cada modelo.
            )

            content_response = response.choices[0].message.content.strip()
            return content_response
        except Exception as e:
            print(f"Erro ao enviar mensagem para o Groq: {e}")
            return e
        
    def exception_handler(self, exception: Exception) -> float | Exception:
        """Essa função vai tratar os erros do groq
        - 429 (rate_limit): retorna o tempo de espera
        - 400 (json_validate_failed): retorna 60 segundos como tempo de espera
        - outros erros: retorna a mensagem de erro"""
        
        status_code = getattr(exception, "status_code", None)
        error_message = str(exception)

        wait_time = float(60)

        if status_code == 429:
            match = re.search(r"Please try again in \s+(\d+)\s*s", error_message, re.IGNORECASE)
            if match:
                wait_time = float(match.group(1))
                return wait_time
            
        elif status_code == 400 and "json_validate_failed" in error_message:
            return wait_time
        
        else:
            return exception