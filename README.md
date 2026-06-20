---
title: Campus Multiplataforma LLM
app_port: 8501
tags: streamlit
license: agpl-3.0
---

# Detector de Fake News Campus Multiplataforma

**Poderosa IA capaz de detectar fake news sobre assuntos gerais.**

O Detector de Fake News do Campus Multiplataforma trata-se de um projeto de pesquisa que visa apoiar alunos de jornalismo e usuários do aplicativo Campus Multiplataforma a se informarem e conseguirem destinguir noticias reais de notícias falsas.

## Porque esse projeto existe?

Levando em conta a velocidade da disceminação de desinformação e notícias falsas na rede, esse projeto foi desenvolvido visando ajudar as pessoas a reconhecer possiveis fake news que possam estar sendo disseminadas. O objetivo desse projeto é:

* Desmentir notícias falsas
* Apoiar jornalistas na detecção de notícias falsas
* Instruir os usuários e seguidores do Campus multiplataforma sobre eventuais notícias com viés de enganação.

## Informações técnicas:

* **Backend**: Python 3.10+
* **Web Framework**: Streamlit
* **AI APIs**:
    * Groq

## Bora Começar

**Prerequisitos**:

* Python 3.10 ou maior
* Git (opcional, para clonar)
* uv 0.9.30
* Chaves de API:
    * Chave de API Groq

**Configurando**:

1. **Clone o repositório (ou baixe os arquivos):**

    ```bash
    git clone https://github.com/RafaBonach/detector-fake-news-jornal-campus.git
    cd detector-fake-news-jornal-campus
    ```

2. **Cria e ativa o ambiete virtual:**

    ```bash
    python -m venv venv
    # On macOS/Linux:
    source venv/bin/activate
    # On Windows:
    .\venv\Scripts\activate
    ```

3. **Instala as dependências**

    ```bash
    uv sync
    ```

4. **Configura a chave de API**
    * Copie `.env.exemple` em um arquivo chamado `.env` na raiz do projeto
    * Adicione sua chave de API (mais instruções  no arquivo de exemplo)

        ```dotenv
        HUGGINGFACE_API_KEY=your_huggingface_api_key

        GOOGLE_PROJECT_ID=your_google_project_id
        GOOGLE_API_KEY=your_google_api_key

        GROQ_API_KEY=your_groq_api_key
        GROQ_API_KEY_ANALYSER=your_groq_api_key

        OPENROUTER_API_KEY=your_openrouter_api_key
        ```

5. **Configurando os prompts**
    * Reveja `src/config_base.py` para modificar os prompts.

## Rodando a aplicação

Esse projeto consiste em um servidor web (`src/stramlit_app.py`) para visualizar interagir com a LLM e um script (`src/llm_analyser/analyser.py`) para analisar o desempenho dos modelos.

* **Comandos:**

    * Webapp:
        ```bash
        # Usando Makefile
        make streamlit
        # Usando comando direto
        uv run streamlit run src/streamlit_app.py
        ```

    * Analisador:
        ```bash
        # Usando Makefile
        make analyse
        # Usando comando direto
        uv run python src/llm_analyser/analyser.py
        ```

## Rodando no Docker

Alternativamente a execução local, você pode rodar o projeto usando Docker.
O projeto possui os arquivos `Dockerfile` e `compose.yml` que ajudaram na inicialização do docker.
O arquivo `Makefile` também possui comando que simplificação a inicialização.

**Comandos Make disponíveis:**

* `make build`: Constroi a imagem Docker.
* `make up`: Inicia a aplicação web.
* `make run-web`: Roda a aplicação web no docker.
* `make lint`: Roda o verificador de código.
* `make format`: Roda o formatador de código.

**Construa a imagem do Docker:**

```bash
make build
```

**Rode a aplicação usando Docker Compose:**

Para rodar a aplicação web, use:

```bash
make up
```

Depois de rodar esse comando, você poderá acessar a interface web pelo caminho `http://localhost:8501`.

Você pode encerrar a aplicação com `CTRL+C` na linha de comando momentos depois.

## Licença
Esse projeto está licenciado por **GNU Affero General Public License v3.0 (AGPLv3)**.

Resumindo a licença, você pode modificar, distribuir esse software ou rodar uma versão moficada como um serviço de internet em que os usuário irão interagir com o software, você só **deve** disponibilizar o código-fonte completo correspondente à sua versão sob a licença AGPLv3.

Você pode ler o texto completo da licença aqui:
[https://www.gnu.org/licenses/agpl-3.0.html](https://www.gnu.org/licenses/agpl-3.0.html)