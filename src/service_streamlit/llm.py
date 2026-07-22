"""Compatibilidade com a camada Streamlit.

Este wrapper preserva a API existente enquanto delega a lógica para a
camada pública reutilizável.
"""

from campus_multiplataforma_llm.chat_service import ChatService

from service_streamlit.utils import get_api_key

class LLMService:
    """Ponte de compatibilidade entre Streamlit e a camada pública de chat."""

    def __init__(self, model_name: str):
        """Inicializa o serviço de UI com o modelo selecionado.

        Args:
            model_name: Nome do modelo escolhido pelo usuário na interface.

        Raises:
            ValueError: Quando a chave de API não está disponível nos segredos
            do Streamlit.
        """

        self.model_name = model_name
        self.__api_key__ = get_api_key()
        self._chat_service = ChatService(model_name=model_name, api_key=self.__api_key__)

    def answer_question(self, user_question, history=None, params=None):
        """Encaminha a pergunta para a camada pública de chat.

        Args:
            user_question: Pergunta atual do usuário.
            history: Histórico opcional de mensagens no formato de chat.
            params: Parâmetros opcionais para a chamada ao provedor.

        Returns:
            str: Texto da resposta gerada pelo modelo.

        Raises:
            Exception: Repropaga exceções da chamada ao serviço de LLM.
        """

        return self._chat_service.answer_question(user_question, history=history, params=params)