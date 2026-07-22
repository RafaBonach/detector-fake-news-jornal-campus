from fastapi.testclient import TestClient

from campus_multiplataforma_llm import ChatResponse
from campus_multiplataforma_llm.chat_service import ChatService
from campus_multiplataforma_llm_api.main import app


client = TestClient(app)


def test_health_endpoint_reports_status():
    response = client.get("/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_models_endpoint_lists_catalog(monkeypatch):
    monkeypatch.delenv("LLM_DEFAULT_MODEL", raising=False)

    response = client.get("/models")

    assert response.status_code == 200
    body = response.json()
    assert "groq/compound" in body["models"]
    assert body["default_model"] in body["models"]


def test_chat_requires_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setenv("STREAMLIT_SECRETS_FILE", "/tmp/campus-multiplataforma-missing-secrets.toml")

    response = client.post("/chat", json={"message": "teste"})

    assert response.status_code == 500
    assert response.json()["detail"]["error"] == "missing_api_key"


def test_chat_success_with_mock(monkeypatch):
    monkeypatch.setenv("GROQ_API_KEY", "fake-key")
    monkeypatch.setenv("STREAMLIT_SECRETS_FILE", "/tmp/campus-multiplataforma-missing-secrets.toml")

    def _fake_ask(self, user_question, history=None, params=None):
        return ChatResponse(
            content=f"resposta para: {user_question}",
            model_name=self.model_name,
            messages=[{"role": "system", "content": "base"}, {"role": "user", "content": user_question}],
        )

    monkeypatch.setattr(ChatService, "ask", _fake_ask)

    response = client.post(
        "/chat",
        json={
            "message": "Essa notícia é verdadeira?",
            "model_name": "groq/compound",
            "history": [{"role": "user", "content": "mensagem anterior"}],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["response"] == "resposta para: Essa notícia é verdadeira?"
    assert body["model_name"] == "groq/compound"