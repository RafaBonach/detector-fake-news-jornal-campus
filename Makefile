# Load environment variables from .env file if it exists or use .env.example as fallback
ifneq (,$(wildcard .env))
    include .env
    export $(shell sed 's/=.*//' .env)
else
    include .env.example
    export $(shell sed 's/=.*//' .env.example)
endif

COMPOSE_COMMAND= docker compose --env-file .env -f compose.yml
PYTHON_COMMAND= docker run --rm --network host --env-file .env -e PYTHONPATH=/app/src -e docker-web:latest .venv/bin/python

up:
	$(COMPOSE_COMMAND) up -d
down:
	$(COMPOSE_COMMAND) down
logs:
	$(COMPOSE_COMMAND) logs -f
ps:
	$(COMPOSE_COMMAND) ps
build:
	$(COMPOSE_COMMAND) build --no-cache
bash:
	$(COMPOSE_COMMAND) exec web bash
run-web:
	$(PYTHON_COMMAND) streamlit run src/streamlit_app.py
run-analyse:
	$(PYTHON_COMMAND) python src/llm_analyser/analyser.py

lint:
	uv run ruff check . 

format:
	uv run ruff check . --fix

streamlit:
	uv run streamlit run src/streamlit_app.py

analyse:
	uv run python src/llm_analyser/analyser.py

.PHONY: up down logs ps build bash migrate run app streamlit analyse
