pt_br = " Responda exclusivamente em português brasileiro. Nunca responda em inglês."
think = " /think"
no_think = " /no_think"
MODELS = {
    "groq": [
            'allam-2-7b',
            "groq/compound",
            "groq/compound-mini",
            "llama-3.1-8b-instant",
            "meta-llama/llama-4-scout-17b-16e-instruct",
            "meta-llama/llama-prompt-guard-2-22m",
            "meta-llama/llama-prompt-guard-2-86m",
            "openai/gpt-oss-120b",
            "openai/gpt-oss-20b",
            "openai/gpt-oss-safeguard-20b",
            "qwen/qwen3-32b",
    ],
    "huggingface": [
        "openai/gpt-oss-20b:groq",
        "openai/gpt-oss-safeguard-20b:groq",
        "openai/gpt-oss-120b:groq",
        "Qwen/Qwen3-32B:groq",
        "meta-llama/Llama-3.3-70B-Instruct:groq",
    ],
    "openrouter": [
        "openrouter/owl-alpha",
        "google/gemma-4-26b-a4b-it:free"
        "google/gemma-4-31b-it:free",
        "nvidia/nemotron-3-super-120b-a12b:free",
        "nvidia/nemotron-3-nano-omni-30b-a3b-reasoning:free",
        "qwen/qwen3-next-80b-a3b-instruct:free",
        "qwen/qwen3-coder:free",
        "openai/gpt-oss-20b:free",
        "openai/gpt-oss-120b:free",
        "meta-llama/llama-3.2-3b-instruct:free",
        "meta-llama/llama-3.3-70b-instruct:free",
    ]
}

PROMPTS = {
    "base":{
        "campusito": "Você é um classificador binário de desinformação. "
        "Classifique a seguinte afirmação como 'Falsa' ou 'Verdadeira'." + pt_br + ":"
        "\n\nMensagem : {question}.\n\n"
        "Retorne no formato abaixo:\n"
        "Classificação: FALSA ou VERDADEIRA\n"
        "Justificativa: no máximo 2 frases curtas.\n\n"
        "Regras obrigatórias:\n"
        "1) Não invente fatos, cargos, datas, números ou nomes.\n"
        "2) Não adicione detalhes que não sejam estritamente necessários para justificar a classificação.\n"
        "3) Se não tiver confiança em um detalhe, diga explicitamente: 'Não tenho evidência suficiente para esse detalhe'.\n"
        "4) Não use linguagem especulativa.",

        "zero-shot": "Você é um classificador binário de desinformação. "
        "Classifique a seguinte afirmação como 'Falsa' ou 'Verdadeira':"
        "\n\nMensagem : {question}.\n\n"
        "Retorne sem explicação adicional exatamente uma palavra: falsa ou verdadeira." + pt_br,
    },
    "definition": ""
}