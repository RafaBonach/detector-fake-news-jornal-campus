"""Serviço público de chat independente de Streamlit.

Este módulo concentra a lógica reutilizável para consumo por outros projetos.
"""

from dataclasses import dataclass

from groq import Groq

from config.prompts import BASE as PROMPTS_BASE
from config.settings import MODELS as MODELS_LIST


@dataclass(slots=True)
class ChatResponse:
    """Representa a saída padronizada do serviço de chat.

    Attributes:
        content: Texto final retornado pelo modelo.
        model_name: Nome do modelo usado para a geração.
        messages: Lista de mensagens enviada ao provedor no formato
            ``[{"role": "...", "content": "..."}]``.
    """

    content: str
    model_name: str
    messages: list[dict[str, str]]


def get_available_models() -> list[str]:
    """Retorna a lista de modelos disponíveis para consumo externo.

    Returns:
        list[str]: Modelos suportados pela aplicação.
    """

    return list(MODELS_LIST)


def build_base_prompt(key_base: str = "campusito") -> list[dict[str, str]]:
    """Monta o prompt base de sistema a partir da chave informada.

    Args:
        key_base: Chave que identifica o prompt em ``config.prompts.BASE``.

    Returns:
        list[dict[str, str]]: Lista com uma mensagem inicial no formato
            esperado pelo provedor.

    Raises:
        ValueError: Quando ``key_base`` não existe no catálogo de prompts.
    """

    if key_base not in PROMPTS_BASE:
        raise ValueError(
            f"Chave '{key_base}' não encontrada em prompts_base. Opções disponíveis: {list(PROMPTS_BASE.keys())}"
        )

    return [{"role": "system", "content": PROMPTS_BASE[key_base]}]


def append_user_message(base_prompt: list[dict[str, str]], question: str) -> list[dict[str, str]]:
    """Adiciona uma mensagem de usuário ao histórico de prompt.

    Args:
        base_prompt: Histórico atual de mensagens.
        question: Pergunta textual enviada pelo usuário.

    Returns:
        list[dict[str, str]]: Novo histórico com a mensagem do usuário.
    """

    updated_prompt = base_prompt.copy()
    updated_prompt.append({"role": "user", "content": question})
    return updated_prompt


class ChatService:
    """Serviço reutilizável para gerar respostas via Groq.

    Esta classe encapsula construção de prompt, montagem de histórico e
    chamada ao provedor de LLM.
    """

    def __init__(self, model_name: str, api_key: str, prompt_key: str = "campusito"):
        """Inicializa o serviço de chat.

        Args:
            model_name: Nome do modelo que será chamado no provedor.
            api_key: Chave de autenticação da API Groq.
            prompt_key: Chave do prompt base carregado de ``config.prompts``.

        Raises:
            ValueError: Quando ``api_key`` não é informada.
            ValueError: Quando ``prompt_key`` não existe no catálogo de prompts.
        """

        if not api_key:
            raise ValueError("api_key é obrigatória para inicializar ChatService.")

        self.model_name = model_name
        self.api_key = api_key
        self.prompt_template = build_base_prompt(prompt_key)

    def _chat_groq(self, messages: list[dict[str, str]], params: dict | None = None) -> str:
        """Envia mensagens para a API Groq e retorna o texto gerado.

        Args:
            messages: Sequência de mensagens no formato de chat.
            params: Parâmetros opcionais para inferência, como ``top_p`` e
                ``max_completion_tokens``.

        Returns:
            str: Conteúdo textual gerado pelo modelo.

        Raises:
            Exception: Qualquer exceção retornada pelo cliente Groq.
        """

        groq_client = Groq(api_key=self.api_key)

        try:
            response = groq_client.chat.completions.create(
                messages=messages,
                model=self.model_name,
                seed=42,
                top_p=params.get("top_p") if params and "top_p" in params else 1,
                max_completion_tokens=params.get("max_completion_tokens") if params and "max_completion_tokens" in params else 4700,
            )
            return response.choices[0].message.content.strip()
        except Exception as exc:
            print(f"Erro ao enviar mensagem para o Groq: {exc}")
            raise exc

    def build_messages(self, user_question: str, history: list[dict[str, str]] | None = None) -> list[dict[str, str]]:
        """Monta o histórico final de mensagens para uma chamada ao modelo.

        Args:
            user_question: Pergunta atual enviada pelo usuário.
            history: Histórico opcional de interações anteriores.

        Returns:
            list[dict[str, str]]: Sequência final com prompt base, histórico e
            pergunta atual.
        """

        messages = self.prompt_template.copy()
        if history:
            messages.extend(history)
        return append_user_message(messages, user_question)

    def ask(
        self,
        user_question: str,
        history: list[dict[str, str]] | None = None,
        params: dict | None = None,
    ) -> ChatResponse:
        """Executa a geração da resposta e retorna resultado estruturado.

        Args:
            user_question: Pergunta atual do usuário.
            history: Histórico opcional de conversa.
            params: Parâmetros opcionais de geração para o provedor.

        Returns:
            ChatResponse: Objeto com texto final, modelo utilizado e mensagens
            enviadas ao provedor.

        Raises:
            Exception: Repropaga exceções geradas pelo provedor de LLM.
        """

        messages = self.build_messages(user_question, history=history)
        answer = self._chat_groq(messages, params=params)
        return ChatResponse(content=answer, model_name=self.model_name, messages=messages)

    def answer_question(self, user_question: str, history: list[dict[str, str]] | None = None, params: dict | None = None) -> str:
        """Retorna somente o conteúdo textual da resposta.

        Método de compatibilidade para consumidores que esperam uma ``str``
        em vez de ``ChatResponse``.

        Args:
            user_question: Pergunta atual do usuário.
            history: Histórico opcional de conversa.
            params: Parâmetros opcionais de geração para o provedor.

        Returns:
            str: Resposta textual gerada pelo modelo.

        Raises:
            Exception: Repropaga exceções geradas pelo provedor de LLM.
        """

        return self.ask(user_question, history=history, params=params).content