FROM python:3.13.5-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
RUN mkdir /app
WORKDIR /app
COPY . .
RUN uv sync
EXPOSE 5000

HEALTHCHECK CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/_stcore/health', timeout=3).read()"

ENTRYPOINT ["uv", "run", "streamlit", "run", "src/streamlit_app.py", "--server.port=5000", "--server.address=0.0.0.0"]