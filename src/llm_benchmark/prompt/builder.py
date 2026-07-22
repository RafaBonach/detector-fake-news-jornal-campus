import config.prompts as PROMPTS

class PromptBuilder:
    def __init__(self, base_prompt_name: str):
        self.base_prompt_name = base_prompt_name
        self.__prompt__ = [
            {
                "role": "system",
                "content": PROMPTS.BASE[self.base_prompt_name]
            }
        ]

    def add_prompts(self, questions: list[str]) -> None:
        """Adiciona ao prompt uma nova pergunta do usuário"""
        q = ""
        if questions != []:
            for i_quest in range(len(questions)):
                q += f"Pergunta {i_quest + 1}: " + questions[i_quest] + "\n\n"
            self.__prompt__.append({
                "role": "user",
                "content": q
            })
        else:
            raise ValueError("A lista de perguntas está vazia. Não é possível adicionar ao prompt.")
    
    def get_prompt(self) -> list[dict[str, str]]:
        """Retorna o prompt completo"""
        return self.__prompt__