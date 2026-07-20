"""Serviço responsável pela comunicação com o provedor de LLM.

O módulo monta o prompt, envia a requisição ao modelo e devolve a
resposta final para a camada de interface.
"""

from groq import Groq

from service_streamlit.utils import get_api_key, set_base_prompt, update_prompt

class LLMService:
    """Serviço que encapsula a comunicação com  provedor de LLM (Groq).
    
    Cada instância representa uma "sessão" configurada para um modelo específico: monta o prompt inicial, guarda a chave de API e expões o método `answer_question` para gerar respostas a partir de perguntas do usuário.
    """
    def __init__(self, model_name: str):
        """Inicializa o serviço com o modelo selecionado pelo usuário."""

        self.model_name = model_name
        self.prompt_template = set_base_prompt()
        self.__api_key__ = get_api_key()
    
    def __chat_groq__(self, messages: list[dict[str, str]] | str, params: dict = None) -> str:
        """Envia as mensagens para a API Groq e retorna o texto gerado.
        
        Args:
            messages: Histórico de mensagens no formato esperado pela API (lista de dicts com "role" e "content"), ou uma string única.
            params: Parâmetros opcionais da camada. Chaves aceitas:
                - "top_p": controla a diversidade da resposta (padrão: 1)
                - "max_completion_tokens": limite de tokens na resposta (padrão: 4700)
                
        Returns:
            O texto da resposta gerada pelo modelo, já sem espaços extras.
            
        Raises:
            Exception: Repassa ualquer erro da API do Groq (rede, autenticação, limite de uso, etc.) após registrar no log.
        """

        groq_client = Groq(api_key=self.__api_key__)

        try:
            response = groq_client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                seed=42,
                top_p=params.get("top_p") if params and "top_p" in params else 1,
                max_completion_tokens=params.get("max_completion_tokens") if params and "max_completion_tokens" in params else 4700,
            )

            content_response = response.choices[0].message.content.strip()
            return content_response
        except Exception as e:
            print(f"Erro ao enviar mensagem para o Groq: {e}")
            raise e

    def answer_question(self, user_question):
        """Monta o prompt final, chama o modelo e devolve a resposta."""

        prompt = update_prompt(self.prompt_template, user_question)

        answer = self.__chat_groq__(prompt)

        if isinstance(answer, ValueError):
            print("Erro ao chamar o modelo LLM:", answer)
            raise answer
        
        return answer