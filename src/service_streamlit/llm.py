# bibliotecas de sistema
import os
import re
import torch

from service_streamlit.utils import set_base_prompt, update_prompt, select_prompt, remove_think, normalize_boolean_answer, get_api_key
import config_base as config

#from transformers import AutoModelForCausalLM, AutoTokenizer
from groq import Groq

#from google import genai

from huggingface_hub import InferenceClient as InfClient

from langchain_openrouter import ChatOpenRouter

from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

class LLMService:
    def __init__(self, model_name):
        self.model_name = model_name
        self.provider = None
        self.prompt_template = set_base_prompt() # Prompt Base
        self.api_key = None

        # self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
    
        """
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype="auto",
            device_map="auto",
        )
        """
        
        self.__models_available__ = []
        self.__providers_available__ = {prov: None for prov in config.MODELS.keys()}
    
    def call_groq(self, prompt, seed=None):
        groq_client = Groq(api_key=self.api_key)

        response = groq_client.chat.completions.create(
            model=self.model_name,
            messages=prompt,
            seed=seed,
        )

        return response.choices[0].message.content.strip()

    def __select_provider__(self):
        provider = ""
        for provider, models in config.MODELS.items():
            if self.model_name in models:
                self.provider = provider
                break

    def __call__(self, prompt):
        if self.provider is None:
            self.__select_provider__()

        # debug
        print(f"\n\n\nModelo {self.model_name} selecionado utilizando o provedor {self.provider}.\n\n\n")
        
        self.api_key = get_api_key(self.provider)

        # debug
        if self.api_key is None:
            print(f"\n\n\n⚠️ Atenção: Nenhuma chave de API encontrada para o provedor {self.provider}. Verifique as variáveis de ambiente.\n\n\n")
        else:
            print(f"\n\n\nUma chave de API foi encontrada para o provedor {self.provider}.\n\n\n")

        if self.provider == "groq":
            return self.call_groq(prompt)
        else:
            raise ValueError(f"Modelo {self.model_name} não associado a nenhum provedor conhecido.")


    def answer_question(self, user_question):
        prompt = update_prompt(self.prompt_template, user_question)

        answer = self.__call__(prompt)

        if not answer:
            print("Nenhuma resposta encontrada para a pergunta.")
            return "Desculpe, não consegui encontrar uma resposta para sua pergunta."
        
        return answer