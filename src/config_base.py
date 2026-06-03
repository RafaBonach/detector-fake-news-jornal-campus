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

MODELS_CONFIG = {
    "meta-llama/llama-4-scout-17b-16e-instruct": {
        "max_estimated_tokens": 17000    
    },
    "openai/gpt-oss-120b": {
        "max_estimated_tokens": 4700
    },
    "openai/gpt-oss-20b": {
        "max_estimated_tokens": 4700
    },
    "openai/gpt-oss-safeguard-20b": {
        "max_estimated_tokens": 4700
    }
}

PROMPTS = {
    "base":{
        "campusito": "Você é um classificador binário de desinformação. "
            "Classifique a seguinte afirmação como 'Falsa' ou 'Verdadeira'." + pt_br + ":"
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
            "na mesma ordem.\n\n",
        "few-shot": """Você é um classificador binário de informações.\n
            Classifique CADA notícia abaixo como verdadeira (1) ou falsa (0).\n
            Responda SOMENTE com um objeto JSON válido, sem texto adicional, sem markdown, sem explicações.\n
            Formato obrigatório:\n
            {"classifications": [<int>, <int>, ...]}\n
            A lista deve ter exatamente o mesmo número de elementos que as notícias fornecidas, 
            na mesma ordem.\n\n

            Baseie sua classificação no seguinte exemplo:\n\n

            Exemplo 1: Mensagem: O CDC (Centro de Controle e Prevenção de Doenças) relata atualmente 99.031 mortes. 
            Em geral, as discrepâncias nos números de óbitos entre diferentes fontes são pequenas e explicáveis. 
            O número de mortes hoje gira em torno de 100.000 pessoas.\n
            "classifications": 1\n
            Exemplo 2: Mensagem: Retratação - Hidroxicloroquina ou cloroquina com ou sem um macrolídeo para o 
            tratamento da COVID-19: uma análise de registro multinacional - The Lancet https://t.co/L5V2x6G9or.\n
            "classifications": 0\n\n"""

    },
    "definition": """Notícias Falsas (fake news): De acordo com Tandoc et al. (2018), notícias falsas
                referem-se a conteúdo criado e disseminado deliberadamente com a intenção de enganar o público, 
                frequentemente para obter ganhos financeiros, políticos ou de outra natureza. 
                Esses artigos imitam notícias reais em formato, mas não têm qualquer compromisso com a precisão factual. 
                Ao contrário de outras formas de desinformação, como boatos ou sátiras, as notícias falsas 
                são elaboradas para parecerem credíveis, enquanto enganam o público propositalmente.\n\n
                
                Notícias Verdadeiras (true news): Notícias verdadeiras, conforme definido por Kovach e Rosenstiel (2001), 
                seguem princípios jornalísticos fundamentais, baseando-se em rigorosa verificação de fatos, fontes verificáveis 
                e transparência. O objetivo principal é informar o público com precisão e imparcialidade, 
                com um forte compromisso com a verdade, evitando a manipulação ou distorção dos fatos.\n"""
}
