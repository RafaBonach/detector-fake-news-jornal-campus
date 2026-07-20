pt_br = " Responda exclusivamente em português brasileiro. Nunca responda em inglês."

n_noticias = 102

limitante = f"Você receberá exatamente {n_noticias} notícias. Sua resposta DEVE conter exatamente {n_noticias} números. Se retornar menos ou mais que {n_noticias} classificações, sua resposta estará incorreta."

instrucao_base = "Você é um classificador binário de desinformação. Classifique CADA notícia a seguinte "

benchmark_base = """
Você é um classificador binário de desinformação. Classifique CADA notícia a seguinte como verdadeira (1) ou falsa (0).\n
Responda SOMENTE com um objeto JSON válido, sem texto adicional, sem markdown, sem explicações.\n
Formato obrigatório:\n
{'classifications': [<int>, <int>, ...]}\n
A lista deve ter exatamente o mesmo número de elementos que as notícias fornecidas, na mesma ordem.\n\n
"""

BASE = {
    "campusito": instrucao_base + "como 'Falsa' ou 'Verdadeira'." + pt_br + ":"
        "Retorne no formato abaixo:\n"
        "Classificação: FALSA ou VERDADEIRA\n"
        "Justificativa: no máximo 2 frases curtas.\n\n"
        "Regras obrigatórias:\n"
        "1) Não invente fatos, cargos, datas, números ou nomes.\n"
        "2) Não adicione detalhes que não sejam estritamente necessários para justificar a classificação.\n"
        "3) Se não tiver confiança em um detalhe, diga explicitamente: 'Não tenho evidência suficiente para esse detalhe'.\n"
        "4) Não use linguagem especulativa.",

    "zero-shot": benchmark_base + limitante,
    "few-shot": benchmark_base + limitante + """\n\n

        Tenha base as seguintes definições de notícias falsas e verdadeiras para classificar as notícias fornecidas:\n\n

        Notícias Falsas (fake news): De acordo com Tandoc et al. (2018), notícias falsas 
        referem-se a conteúdo criado e disseminado deliberadamente com a intenção de enganar o público, 
        frequentemente para obter ganhos financeiros, políticos ou de outra natureza. 
        Esses artigos imitam notícias reais em formato, mas não têm qualquer compromisso com a precisão factual. 
        Ao contrário de outras formas de desinformação, como boatos ou sátiras, as notícias falsas 
        são elaboradas para parecerem credíveis, enquanto enganam o público propositalmente.\n\n
        
        Notícias Verdadeiras (true news): Notícias verdadeiras, conforme definido por Kovach e Rosenstiel (2001), 
        seguem princípios jornalísticos fundamentais, baseando-se em rigorosa verificação de fatos, fontes verificáveis 
        e transparência. O objetivo principal é informar o público com precisão e imparcialidade, 
        com um forte compromisso com a verdade, evitando a manipulação ou distorção dos fatos.\n\n

        Baseie sua classificação no seguinte exemplo:\n\n

        Exemplo 1: Mensagem: O CDC (Centro de Controle e Prevenção de Doenças) relata atualmente 99.031 mortes. 
        Em geral, as discrepâncias nos números de óbitos entre diferentes fontes são pequenas e explicáveis. 
        O número de mortes hoje gira em torno de 100.000 pessoas.\n
        Resposta: {'classifications': [1]}\n\n

        Exemplo 2: Mensagem: Retratação - Hidroxicloroquina ou cloroquina com ou sem um macrolídeo para o 
        tratamento da COVID-19: uma análise de registro multinacional - The Lancet https://t.co/L5V2x6G9or.\n
        Resposta: {'classifications': [0]}\n\n

        Exemplo 3: Mensagem: O presidente do Brasil, lula, desembarca no rj hostilizado pela populacao. Os hospedes surpreendem o presidente de dentro do hotel sob gritos "Lula ladrao, lugar de bandido é na prisao". Apesar do tumutuado desembarte no aeroporto do rio janeiro, petista nao se incomodou e ainda mostrou seu sorriso amarelado. \n
        Resposta: {'classifications': [0]}\n\n

        Exemplo 4: Mensagem: O deputado celso jacob, que foi flagrado com biscoito de queijo dentro da cueca, retornar ao presidio. O episodio aconteceu no ultimo domingo quando voltava para a papuda apos o saidão do fim semana em tres rios. O deputado foi preso por falsificacao de documento publico. Após a dispensa, deputado federal celso jacob foi flagrado com dois pacotes de biscoito de queijo provolone escondidos dentro da cueca. Após o ocorrido, o deputado retornar ao centro de detencao provisoria da papuda do distrito federal, apos a saida de final de semana, autorizada pela justica. o episodio aconteceu no ultimo domingo segundo dados da subsecretaria de sistema penitenciario sesipe, ligada secretaria seguranca publica. Houve irregularidade identificada durante processo de revista. Por conta disso, o parlamentar foi levado ao setor de isolamento onde ficara sete dias. A vara de execucoes penais do tribunal de justica do distrito federal e territorios, tjdft, ja foi comunicada do fato e tambem foi aberto inquerito disciplinar para apurar caso de punicao. O casos pode chegar a 30 dias de isolamento, alem da perda do beneficios. A vep informa em nota "a subsecretaria ressaltou que e proibida a entrada, pelos internos, de qualquer objeto ou alimento no presidio sem autorizacao. A entrada de alimentos so possivel por meio da familia durante o periodo de visita". assessoria de celso jacob disse que ele levou alimentos para atender recomendacoes medicas de se alimentar a cada tres horas. jacob foi preso no inicio junho no aeroporto de brasilia, sob regime semiaberto determinada pela primeira turma do supremo tribunal federal por falsificacao de documento publico de dispensa de licitacao. o peemedebista, prefeito de tres rios do sul, rj, governou a cidade por dois mandatos. no fim de junho, o juiz valter andre bueno araujo da vara de execucoes penais do distrito federal autorizou ao deputado deixar presidio durante dia para trabalhar como parlamentar na camara dos deputados.
        Resposta: {'classifications': [1]}\n\n
        """,
    "gpk": benchmark_base + limitante + """\n\n
        Tenha base as seguintes definições de notícias falsas e verdadeiras para classificar as notícias fornecidas:\n\n

        Notícias Falsas (fake news): De acordo com Tandoc et al. (2018), notícias falsas 
        referem-se a conteúdo criado e disseminado deliberadamente com a intenção de enganar o público, 
        frequentemente para obter ganhos financeiros, políticos ou de outra natureza. 
        Esses artigos imitam notícias reais em formato, mas não têm qualquer compromisso com a precisão factual. 
        Ao contrário de outras formas de desinformação, como boatos ou sátiras, as notícias falsas 
        são elaboradas para parecerem credíveis, enquanto enganam o público propositalmente.\n\n
        
        Notícias Verdadeiras (true news): Notícias verdadeiras, conforme definido por Kovach e Rosenstiel (2001), 
        seguem princípios jornalísticos fundamentais, baseando-se em rigorosa verificação de fatos, fontes verificáveis 
        e transparência. O objetivo principal é informar o público com precisão e imparcialidade, 
        com um forte compromisso com a verdade, evitando a manipulação ou distorção dos fatos.\n\n

        Base de conhecimento:\n\n

        Uma notícia falsa frequentemente apresenta uma ou mais das seguintes características:\n\n

        - Alegações sem qualquer evidência verificável.\n
        - Uso de dados verdadeiros apresentados fora de contexto.\n
        - conteúdo gerado por inteligência artificial.\n
        - Atribui declarações a especialistas inexistentes ou sem credenciais.\n
        - Contradiz informações amplamente confirmadas por órgãos oficiais ou instituições científicas.\n
        - Apresenta estatísticas sem indicar sua origem.\n
        - Noticias importantes com pouca difusão na mídia ou ausência de cobertura por veículos de comunicação confiáveis.\n
        - Noticas antigas sendo circuladas como recentes.\n
        - Mistura fatos verdadeiros com informações falsas para aumentar sua credibilidade.\n
        - Presença de expressões como 'a mídia não quer que você saiba', 'compartilhe antes que apaguem' ou 'verdade escondida'
        - Ausencia da origem de um dado estatistico.

        Uma notícia verdadeira geralmente:\n\n

        - Cita fontes identificáveis.\n
        - Apresenta informações consistentes com órgãos oficiais ou estudos científicos.\n
        - Diferencia fatos de opiniões.\n
        - Mantém linguagem objetiva.\n
        - Possui dados verificáveis.\n
        - Possui poucos ou nenhum erro gramatical ou de digitação.\n

        Para a analise, compare as afirmações presentes em cada notícia com as informações da base de conhecimento.
            Caso a notícia contradiga fatos estabelecidos na base de conhecimento, classifique-a como falsa (0).
            Caso a notícia seja consistente com a base de conhecimento, classifique-a como verdadeira (1).
            Caso existam pequenas diferenças de redação, concentre-se no significado das afirmações, e não na similaridade textual.
            Não forneça justificativas nem explicações.\n\n

        Alguns exemplos de notícias verdadeiras:
        Mensagem: A vacina contra COVID-19 não altera o DNA humano.\n
            Resposta: {'classifications': [1]}\n\n
        
        Mensagem: O Conselho Nacional de Política Energética elevou temporariamente o teor de etanol anidro na gasolina de 30% para 32%.\n
        Resposta: {'classifications': [1]}\n\n

        Alguns exemplos de notícias falsas:
        Mensagem: Anuário diz que nº de homens mortos por mulheres é maior que o de mulheres mortas por homens\n
        Resposta: {'classifications': [0]}\n\n

        Mensagem: Lula quebrou o protocolo e ligou ​direto para Trump para desmascarar a farsa do clã Bolsonaro e ​expôs as ligações da direita com o Comando Vermelho\n
        Resposta: {'classifications': [0]}\n\n
        """

}