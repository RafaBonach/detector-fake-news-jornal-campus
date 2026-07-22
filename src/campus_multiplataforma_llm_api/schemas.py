"""Schemas da API HTTP pública."""

from pydantic import BaseModel, Field


class MessageItem(BaseModel):
    """Representa uma única mensagem no histórico de chat.

    Attributes:
        role: Papel da mensagem, como ``system``, ``user`` ou ``assistant``.
        content: Texto associado ao papel da mensagem.
    """

    role: str = Field(description="Papel da mensagem no chat (system, user, assistant).")
    content: str = Field(description="Conteúdo textual da mensagem.")


class ChatRequest(BaseModel):
    """Payload de entrada utilizado no endpoint ``POST /chat``.

    Attributes:
        message: Mensagem atual enviada pelo usuário.
        model_name: Modelo solicitado; quando ausente, usa modelo padrão.
        prompt_key: Chave para seleção de prompt base.
        history: Histórico anterior de mensagens.
        params: Parâmetros opcionais encaminhados ao provedor de LLM.
    """

    message: str = Field(min_length=1, description="Mensagem atual do usuário.")
    model_name: str | None = Field(default=None, description="Nome do modelo a usar; opcional.")
    prompt_key: str = Field(default="campusito", description="Chave do prompt base.")
    history: list[MessageItem] = Field(default_factory=list, description="Histórico anterior da conversa.")
    params: dict[str, float | int | str | bool] | None = Field(
        default=None,
        description="Parâmetros opcionais para o provedor LLM.",
    )


class ChatResponseBody(BaseModel):
    """Resposta padronizada retornada pelo endpoint ``POST /chat``.

    Attributes:
        response: Texto final gerado pelo modelo.
        model_name: Modelo utilizado durante a geração.
        messages: Histórico completo de mensagens enviado ao provedor.
    """

    response: str
    model_name: str
    messages: list[MessageItem]


class HealthResponse(BaseModel):
    """Estrutura de resposta do endpoint ``GET /health``.

    Attributes:
        status: Estado da API, normalmente ``ok``.
        api_key_configured: Indica se uma chave de API foi resolvida.
    """

    status: str
    api_key_configured: bool


class ModelsResponse(BaseModel):
    """Estrutura de resposta do endpoint ``GET /models``.

    Attributes:
        models: Lista de modelos suportados pela aplicação.
        default_model: Modelo padrão configurado para a API.
    """

    models: list[str]
    default_model: str