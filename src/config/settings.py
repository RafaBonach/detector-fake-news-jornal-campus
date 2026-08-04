"""Configurações base dos modelos disponíveis no projeto.

Este arquivo centraliza a lista de modelos suportados e os limites
estimados de tokens usados pelo restante da aplicação para seleção,
dimensionamento de contexto e validações operacionais.

Attributes:
    MODELS: Catálogo de modelos permitidos para interface e API.
    MODELS_CONFIG: Metadados operacionais por modelo.
"""

# Modelos disponíveis por provedor.
MODELS = [
    "openai/gpt-oss-120b",
    "openai/gpt-oss-20b",
    "openai/gpt-oss-safeguard-20b",
    "qwen/qwen3.6-27b"
]

# Metadados e limites estimados de cada modelo.
MODELS_CONFIG = {
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "max_estimated_tokens": 17000
    },
    "openai/gpt-oss-120b": {
        "max_estimated_tokens": 4700
    },
    "openai/gpt-oss-20b": {
        "max_estimated_tokens": 4700
    },
    "openai/gpt-oss-safeguard-20b": {
        "max_estimated_tokens": 4700
    }
}