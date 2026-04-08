MODELS = {
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
        "zero-shot": """Classify the following statement as 'False ' or 'True ':
        \n Message : {question}.\n Return only the Classification in a single word ( true / false ) 
        without any further explanation :"""
    }
}