from config_base import PROMPTS, MODELS
import re
import os

def select_prompt(prompt_cat= None | str, prompt_typ= None | str) -> str:
    """Construtor de prompt baseado na categoria e no tipo.
    Argumentos:
        prompt_cat (chr | None): B | None -> Base | D -> Base e Definição.
        prompt_typ (str | None): str -> tipo específico | None -> "Campusito".
        
        Se os argumentos forem diferentes de PROMPTS em config_base, será considerado o como None.
    Retorna:
        str: O prompt construído a partir da categoria e tipo.
    """
    
    result_prompt = ""
    
    if prompt_cat == 'D' or prompt_cat == 'd':
        result_prompt = "\n\n"+ PROMPTS["definition"]

    if prompt_typ is not None and prompt_typ in PROMPTS["base"]:
        return PROMPTS["base"][prompt_typ] + result_prompt
    return PROMPTS["base"]["campusito"] + result_prompt

def remove_think(text: str) -> str:
    """Remove blocos de raciocínio explícito do texto gerado pela LLM.
    Argumentos:
        text (str): O texto potencialmente contendo tags de raciocínio, como <think> e </think>.
    Retorna:
        str: O texto limpo, sem blocos de raciocínio.
    """
    cleaned_text = re.sub(r"<think>.*?</think>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    cleaned_text = re.sub(r"</?think>", " ", cleaned_text, flags=re.IGNORECASE)
    return cleaned_text.strip()


def normalize_boolean_answer(answer) -> str:
    """Normaliza a resposta bruta da LLM para um valor booleano textual estrito.

    Parametros:
        answer (str): texto retornado pelo modelo, que pode conter cadeias extras
            (por exemplo, tags de raciocinio) junto de "true" ou "false".

    Retorno:
        str: retorna somente "true" ou "false". Se ambos aparecerem no texto,
            prioriza a ultima ocorrencia; se nenhum aparecer, retorna "false".
    """
    normalized = answer.strip().lower()

    # Remove marcadores comuns de raciocinio explicito.
    normalized = re.sub(r"</?think>", " ", normalized)

    matches = re.findall(r"\b(true|false)\b", normalized)
    if matches:
        return matches[-1]

    if "true" in normalized:
        return "true"
    if "false" in normalized:
        return "false"

    return "false"

def select_model(model: dict) -> tuple[str, str]:
    """Seleciona o modelo a ser utilizado com base no dicionário de modelos disponíveis.
    Argumentos:
        model (dict): O dicionário contendo as informações do modelo.
    Retorna:
        tuple: Uma tupla contendo o provedor e o modelo.
    """
    return str(model.key()), str(model.values())

def get_models(key: str|None = None) -> list[str]:
    """Recupera a lista de modelos disponíveis a partir do dicionário MODELS.
    Retorna:
        list: Uma lista contendo os nomes dos modelos disponíveis.
    """
    if key:
        model_options = MODELS.get(key, [])
        model_options.sort()  # Ordena alfabeticamente
        return model_options
    
    seen = set()
    model_options = []
    for models in MODELS.values():
        for m in models:
            if m not in seen:
                seen.add(m)
                model_options.append(m)
    
    model_options.sort()  # Ordena alfabeticamente
    return model_options

def get_api_key(provider: str) -> str:
    """Recupera a chave de API para o provedor especificado.
    Argumentos:
        provider (str): O nome do provedor para o qual a chave de API é necessária.
    Retorna:
        str: A chave de API correspondente ao provedor.
    """

    if provider == "groq":
        return os.getenv("GROQ_API_KEY")
    elif provider == "groq_analyser":
        return os.getenv("GROQ_API_KEY_ANALYSER")
    elif provider == "huggingface":
        return os.getenv("HUGGINGFACE_API_KEY")
    elif provider == "openrouter":
        return os.getenv("OPENROUTER_API_KEY")
    else:
        raise ValueError(f"Provedor desconhecido: {provider}")

if __name__ == "__main__":
    print(select_prompt())