# bibliotecas de sistema
import os
import time

from service_streamlit.utils import select_prompt

from transformers import AutoModelForCasuaLLM, AutoTokenizer, pipeline, set_seed
import torch

class LLMService:
    def __init__(self, model_name):
        self.model_name = model_name
        self.prompt_template = select_prompt()
    
    def call_llm(self, prompt):
        messages = [{"role": "user", "content": prompt}]
        
        # dtype="auto" -> Aloca o peso do modelo pro dispositivo mais rápido, device_map="auto" -> evita carregamento dos pesos duas vezes
        tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        model = AutoModelForCasuaLLM.from_pretrained(self.model_name, dtype="auto", device_map="auto")

        text = tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
            enable_thinking=True
        )
        model_input = tokenizer([text], return_tensors="pt").to(model.device)

        generated_ids = model.generate(**model_input, max_length=30)
        return tokenizer.batch_decode(generated_ids)[0]
        
        

    def answer_question(self, user_question):
        prompt = self.prompt_template.format(
            question = user_question
        )

        answer = self.call_llm(prompt)

        if not answer:
            print("Nenhuma resposta encontrada para a pergunta.")
            return "Desculpe, não consegui encontrar uma resposta para sua pergunta."
        
        return answer