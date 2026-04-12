pt_br = " A resposta deve ser gerada exclusivamente em português brasileiro."
think = " /think"
no_think = " /no_think"
MODELS = {
    'qwen3-0.6b': {
        'model_id': '"Qwen/Qwen3-0.6B"',
        'api_key': 'EMPTY',
        'enable_thinking': True,
        'max_new_tokens': 32768,
        'do_sample': False,
        'temperature': 0.6,
        'top_p': 0.95,
        'top_k': 20,
        'min_p': 0,
    },
    'gemma -2b': {
        'model_id ': 'google /gemma-2b',
        'model_name ': 'Gemma-2B-Instruct ',
        'model_family ': 'gemma',
        'endpoint_name ': 'jumpstart-dft-hf-llm-gemma-7b-instr-20241103-193822 ',
        'new ': True ,
        'tuned_for ': None
    },
    "gemma-7b": {
        "model_id": "google /gemma-7b",
        "model_name": "Gemma-7B-Instruct ",
        "model_family": "gemma",
        "endpoint_name": 'jumpstart-dft-hf-llm-gemma-7b-instr-20241116-155953 ',
        "new": True ,
        "tuned_for": None
    },
    "llama-3-1-70b": {
        "model_id": "meta-llama/Meta-Llama-3-70B-Instruct ",
        "model_name": "Llama-3-1-70B-Instruct ",
        "model_family": "llama3 ",
        "endpoint_name": "jumpstart-dft-llama-3-1-70b-instruct-20241225-133356 ",
        "new": True ,
        'max_tokens': 7000,
    },
    "deep-seek-32B": {
        "model_id": "deepseek-coder/deepseek-coder-32b",
        "model_name": "deep-seek-32B",
        "model_family": "deepseek",
        "endpoint_name": "jumpstart-dft-deepseek-llm-r1-disti-20250503-175058",
        "new": True ,
        'max_tokens': 1024
    }
}


PROMPTS = {
    "base":{
        "campusito": "Você é um classificador binário de desinformação. "
        "Classifique a seguinte afirmação como 'Falsa' ou 'Verdadeira':"
        "\n\nMensagem : {question}.\n\n"
        "Retorne, destacando, se a afirmação é verdadeira ou falsa. "
        "Elabore uma breve justificativa para a classificação, explicando os motivos pelos quais a afirmação é verdadeira ou falsa." + pt_br + think,

        "zero-shot": "You are a binary misinformation classifier. "
        "Classify the following statement as 'False ' or 'True':"
        "\n\nMensagem : {question}.\n\n"
        "Return without any further explanation exactly one lowercase token: true or false." + pt_br,
    },
    "definition": ""
}