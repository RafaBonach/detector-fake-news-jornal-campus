"""API HTTP para integração do projeto em aplicações externas."""

import os
import tomllib
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from campus_multiplataforma_llm import ChatService, get_available_models
from campus_multiplataforma_llm_api.schemas import (
    ChatRequest,
    ChatResponseBody,
    HealthResponse,
    ModelsResponse,
)

API_TITLE = "Campus Multiplataforma LLM API"
API_VERSION = "0.1.0"

app = FastAPI(title=API_TITLE, version=API_VERSION)


def _cors_origins() -> list[str]:
    """Resolve a lista de origens permitidas para CORS.

    Returns:
        list[str]: Lista de origens obtida de ``CORS_ALLOW_ORIGINS``.
    """

    raw = os.getenv("CORS_ALLOW_ORIGINS", "*")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


cors_origins = _cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _default_model() -> str:
    """Retorna o modelo padrão da API.

    Returns:
        str: Modelo padrão válido. Usa ``LLM_DEFAULT_MODEL`` quando possível
        e faz fallback para o primeiro modelo suportado.
    """

    models = get_available_models()
    configured_model = os.getenv("LLM_DEFAULT_MODEL", models[0])
    if configured_model not in models:
        return models[0]
    return configured_model


def _resolve_secrets_file() -> Path:
    """Resolve o caminho do arquivo de segredos do Streamlit.

    Returns:
        Path: Caminho para o arquivo ``secrets.toml``.
    """

    configured_path = os.getenv("STREAMLIT_SECRETS_FILE")
    if configured_path:
        return Path(configured_path)
    return Path(".streamlit/secrets.toml")


def _api_key_from_streamlit_secrets() -> str | None:
    """Lê ``GROQ_API_KEY`` do arquivo de segredos do Streamlit.

    Returns:
        str | None: Chave encontrada no arquivo ou ``None`` quando ausente,
        inválida ou ilegível.
    """

    secrets_file = _resolve_secrets_file()
    if not secrets_file.exists():
        return None

    try:
        with secrets_file.open("rb") as file:
            data = tomllib.load(file)
    except Exception:
        return None

    api_key = data.get("GROQ_API_KEY")
    if isinstance(api_key, str) and api_key.strip():
        return api_key.strip()
    return None


def _resolve_api_key() -> str | None:
    """Resolve a chave da Groq por ambiente e fallback em arquivo.

    Returns:
        str | None: Valor de ``GROQ_API_KEY`` no ambiente ou no arquivo de
        segredos do Streamlit.
    """

    return os.getenv("GROQ_API_KEY") or _api_key_from_streamlit_secrets()


def _resolve_model(requested_model: str | None) -> str:
    """Valida e resolve o modelo utilizado na requisição.

    Args:
        requested_model: Modelo solicitado pelo cliente, opcional.

    Returns:
        str: Modelo válido para execução.

    Raises:
        HTTPException: Quando o modelo informado não é suportado.
    """

    model = requested_model or _default_model()
    available = get_available_models()
    if model not in available:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "invalid_model",
                "message": "Modelo informado não é suportado.",
                "available_models": available,
            },
        )
    return model


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Retorna status básico de disponibilidade da API.

    Returns:
        HealthResponse: Estado da API e disponibilidade de chave para Groq.
    """

    return HealthResponse(status="ok", api_key_configured=bool(_resolve_api_key()))


@app.get("/models", response_model=ModelsResponse)
def models() -> ModelsResponse:
    """Lista os modelos disponíveis para chamadas de chat.

    Returns:
        ModelsResponse: Catálogo de modelos suportados e padrão corrente.
    """

    return ModelsResponse(models=get_available_models(), default_model=_default_model())


@app.post("/chat", response_model=ChatResponseBody)
def chat(request: ChatRequest) -> ChatResponseBody:
    """Processa uma mensagem de chat e retorna a resposta do modelo.

    Args:
        request: Payload validado com mensagem, histórico e parâmetros.

    Returns:
        ChatResponseBody: Resposta padronizada da geração de chat.

    Raises:
        HTTPException: Erro 500 quando a chave não é encontrada.
        HTTPException: Erro 400 quando o modelo solicitado é inválido.
        HTTPException: Erro 502 quando há falha no provedor LLM.
    """

    api_key = _resolve_api_key()
    if not api_key:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "missing_api_key",
                "message": "Defina GROQ_API_KEY no ambiente ou em .streamlit/secrets.toml para usar o endpoint /chat.",
            },
        )

    model_name = _resolve_model(request.model_name)

    service = ChatService(model_name=model_name, api_key=api_key, prompt_key=request.prompt_key)

    try:
        result = service.ask(
            user_question=request.message,
            history=[item.model_dump() for item in request.history],
            params=request.params,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail={
                "error": "llm_provider_error",
                "message": str(exc),
            },
        ) from exc

    return ChatResponseBody(response=result.content, model_name=result.model_name, messages=result.messages)