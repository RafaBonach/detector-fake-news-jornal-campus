"""Funções utilitárias da camada Streamlit.

Inclui apenas acesso aos segredos do Streamlit e pequenos auxiliares de UI.
"""

import streamlit as st

def get_models() -> list[str]:
    """Retorna os modelos disponíveis para exibição na interface.

    Returns:
        list[str]: Lista de modelos suportados pela aplicação.
    """

    from campus_multiplataforma_llm.chat_service import get_available_models

    return get_available_models()

def get_api_key(provider: str = "GROQ_API_KEY") -> str:
    """Lê a chave de API a partir dos segredos do Streamlit.

    Args:
        provider: Nome da chave dentro de ``st.secrets``.

    Returns:
        str: Valor da chave de API configurada.

    Raises:
        ValueError: Quando o provedor solicitado não existe em
            ``st.secrets``.
    """

    providers_name = st.secrets.keys()
    
    if provider not in providers_name:
        raise ValueError(f"Provedor desconhecido: {provider}. Opções disponíveis: {list(providers_name)}")
    
    secret_key = st.secrets[provider]
    return secret_key
