# Load environment variables from .env only when the file exists.
ifneq (,$(wildcard .env))
	include .env
	export $(shell sed -n 's/=.*//' .env)
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

api:
	@GROQ_KEY=$$(grep -E '^GROQ_API_KEY=' .streamlit/secrets.toml 2>/dev/null | head -n1 | cut -d'=' -f2- | tr -d '"'); \
	if [ -n "$$GROQ_KEY" ]; then export GROQ_API_KEY="$$GROQ_KEY"; fi; \
	uv run uvicorn campus_multiplataforma_llm_api.main:app --host 0.0.0.0 --port 8000 --reload

analyse:
	uv run python src/llm_benchmark/main.py

.PHONY: up down logs ps build bash migrate run app streamlit analyse api
