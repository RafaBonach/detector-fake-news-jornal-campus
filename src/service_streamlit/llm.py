# bibliotecas de sistema
import os
import re
import torch

from service_streamlit.utils import select_prompt

from transformers import AutoModelForCausalLM, AutoTokenizer

class LLMService:
    def __init__(self, model_name):
        self.model_name = model_name
        self.prompt_template = select_prompt()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name,
        )
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto",
        )

    def __normalize_boolean_answer__(self, answer) -> str:
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
    


    def call_llm(self, prompt):
        messages = [{"role": "user", "content": prompt}]

        try:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
                enable_thinking=True,
            )
        except TypeError:
            text = self.tokenizer.apply_chat_template(
                messages,
                tokenize=False,
                add_generation_prompt=True,
            )

        model_input = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        generated_ids = self.model.generate(
            **model_input,
            max_new_tokens=1024,
            do_sample=False,
            temperature=0.01,
            top_p=1.0,
            repetition_penalty=1.0,
        )

        prompt_size = model_input["input_ids"].shape[1]
        new_tokens = generated_ids[:, prompt_size:]
        raw_answer = self.tokenizer.batch_decode(new_tokens, skip_special_tokens=True)[0].strip()
        
        # A resposta bruta.
        #return raw_answer

        # Normaliza a resposta para garantir que seja estritamente "true" ou "false"
        return self.__normalize_boolean_answer__(raw_answer)
    


    def classify_by_logits(self, prompt: str) -> str:
        messages = [{"role": "user", "content": prompt}]
        text = self.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        inputs = self.tokenizer([text], return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model(**inputs)
            next_token_logits = outputs.logits[:, -1, :]

        true_ids = self.tokenizer.encode(" true", add_special_tokens=False)
        false_ids = self.tokenizer.encode(" false", add_special_tokens=False)

        true_score = next_token_logits[0, true_ids[0]].item()
        false_score = next_token_logits[0, false_ids[0]].item()

        return "true" if true_score > false_score else "false"

        
    def answer_question(self, user_question):
        prompt = self.prompt_template.format(
            question = user_question
        )

        answer = self.call_llm(prompt)

        if not answer:
            print("Nenhuma resposta encontrada para a pergunta.")
            return "Desculpe, não consegui encontrar uma resposta para sua pergunta."
        
        return answer

    