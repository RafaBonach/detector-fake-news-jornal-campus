# bibliotecas de sistema
import os
import torch

from service_streamlit.utils import select_prompt, remove_think, normalize_boolean_answer

from transformers import AutoModelForCausalLM, AutoTokenizer

class LLMService:
    def __init__(self, model_name):
        self.model_name = model_name
        self.prompt_template = select_prompt()
        self.api_key = os.getenv("HUGGINGFACE_API_KEY")

        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto",
        )
    


    def call_llm(self, prompt):
        messages = [{"role": "user", "content": prompt}]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        model_input = self.tokenizer([text], return_tensors="pt").to(self.model.device)
        generated_ids = self.model.generate(
            **model_input,
            max_new_tokens=32768,
            temperature=0.6,
            top_p=0.95,
            top_k=20,
            min_p=0,
            repetition_penalty=1.15,         # reduz invenções por repetição
            no_repeat_ngram_size=4,          # evita loops/frases recicladas
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.eos_token_id,
            use_cache=True,
        )

        prompt_size = model_input["input_ids"].shape[1]
        new_tokens = generated_ids[:, prompt_size:]
        raw_answer = self.tokenizer.batch_decode(new_tokens, skip_special_tokens=True)[0].strip()
        
        # A resposta bruta.
        return remove_think(raw_answer)

        # Normaliza a resposta para garantir que seja estritamente "true" ou "false"
        # return normalize_boolean_answer(raw_answer)
    


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

    