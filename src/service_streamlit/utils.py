"""Funções utilitárias compartilhadas pela aplicação Streamlit.

Inclui acesso aos modelos disponíveis, montagem do prompt base e leitura
da chave de API armazenada nos segredos do Streamlit.
"""

from config.prompts import BASE as prompts_list
from config.settings import MODELS as models_list

import streamlit as st

def set_base_prompt(key_base: str = "campusito") -> list[dict[str, str]]:
    """Retorna a mensagem de sistema inicial usada como base do chat.
    
    Args:
        key_base (str): Chave que identifica qual prompt buscar em `prompts_list` (definido em config/prompts.py). Por padão, usa o prompt "campusito".
        
    Returns:
        Uma lista com um único dicionário no formato esperado pela API da Groq, representando a mesangem do "system":
        [{"role": "system", "content": "..."}]
        
    Raises:
        ValueError: Se `key_base` não existir em `prompts_list`.
    """

    if key_base not in prompts_list:
        raise ValueError(f"Chave '{key_base}' não encontrada em prompts_list. Opções disponíveis: {list(prompts_list.keys())}")
    
    base_prompt = [
        {
            "role": "system",
            "content": prompts_list[key_base]
        }
    ]

    return base_prompt

def update_prompt(base_prompt: list[dict[str, str]], question: str) -> list[dict[str, str]]:
    """Adiciona a pergunta do usuário ao histórico de mensagens."""

    updated_prompt = base_prompt.copy()
    updated_prompt.append({
        "role": "user",
        "content": question
    })
    return updated_prompt

def get_models() -> list[str]:
    """Retorna a lista de modelos configurados no projeto.
    
    A lista é definida em config/settings.py (MODELS) e é usada para popular o seletor de modelo na interface do Streamlit.
    
    Returns:
        Lista com os nomes dos modelos configurados.
    """

    return models_list

def get_api_key(provider: str = "GROQ_API_KEY") -> str:
    """Lê a chave de API do provedor nos segredos do Streamlit."""

    providers_name = st.secrets.keys()
    
    if provider not in providers_name:
        raise ValueError(f"Provedor desconhecido: {provider}. Opções disponíveis: {list(providers_name)}")
    
    secret_key = st.secrets[provider]
    return secret_key
