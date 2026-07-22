from campus_multiplataforma_llm import ChatService, get_available_models


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