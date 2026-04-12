from config_base import PROMPTS
import re

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
    
    if prompt_cat is 'D' or prompt_cat is 'd':
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

if __name__ == "__main__":
    print(select_prompt())