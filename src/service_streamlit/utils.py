from src.config_base import PROMPTS

def select_prompt(prompt_typ: str | None = None, prompt_def: str | None = None) -> str:
    """Informe qual será a base do prompt"""
    prompt_def = "base"
    prompt_typ = "zero-shot"
    
    return PROMPTS[prompt_def][prompt_typ]