from types import SimpleNamespace

from campus_multiplataforma_llm import ChatService, get_available_models
from campus_multiplataforma_llm.chat_service import strip_think_blocks


def test_public_models_match_configuration():
    assert get_available_models() == [
        "groq/compound",
        "groq/compound-mini",
        "openai/gpt-oss-120b",
        "openai/gpt-oss-20b",
        "openai/gpt-oss-safeguard-20b",
    ]


def test_chat_service_builds_prompt_with_history():
    service = ChatService(model_name="groq/compound", api_key="dummy-key")

    messages = service.build_messages(
        "Pergunta atual",
        history=[
            {"role": "user", "content": "Pergunta anterior"},
            {"role": "assistant", "content": "Resposta anterior"},
        ],
    )

    assert messages[0]["role"] == "system"
    assert messages[-1] == {"role": "user", "content": "Pergunta atual"}
    assert messages[1:-1] == [
        {"role": "user", "content": "Pergunta anterior"},
        {"role": "assistant", "content": "Resposta anterior"},
    ]


def test_strip_think_blocks_removes_internal_reasoning():
    content = "<think>Raciocínio interno</think>Resposta final"

    assert strip_think_blocks(content) == "Resposta final"


def test_chat_service_strips_think_blocks_from_provider_response(monkeypatch):
    class FakeGroq:
        def __init__(self, api_key):
            self.api_key = api_key
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(
                    create=lambda **kwargs: SimpleNamespace(
                        choices=[
                            SimpleNamespace(
                                message=SimpleNamespace(
                                    content="<think>Raciocínio interno</think>Resposta final"
                                )
                            )
                        ]
                    )
                )
            )

    monkeypatch.setattr("campus_multiplataforma_llm.chat_service.Groq", FakeGroq)

    service = ChatService(model_name="groq/compound", api_key="dummy-key")

    assert service.answer_question("Pergunta atual") == "Resposta final"