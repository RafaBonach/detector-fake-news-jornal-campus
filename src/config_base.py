pt_br = " Responda exclusivamente em português brasileiro. Nunca responda em inglês."
think = " /think"
no_think = " /no_think"

MODELS = {
    "groq": [
        "meta-llama/llama-4-scout-17b-16e-instruct",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-safeguard-20b",
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

        "zero-shot": "Você é um classificador binário de desinformação.\n"
            "Classifique CADA notícia abaixo como verdadeira (1) ou falsa (0).\n"
            "Responda SOMENTE com um objeto JSON válido, sem texto adicional, sem markdown, sem explicações.\n"
            "Formato obrigatório:\n"
            '{"classifications": [<int>, <int>, ...]}\n'
            "A lista deve ter exatamente o mesmo número de elementos que as notícias fornecidas, "
            "na mesma ordem.\n\n"

    },
    "definition": "Definição de fake news:\n",
}
