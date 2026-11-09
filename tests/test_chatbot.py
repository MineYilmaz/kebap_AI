import json

import httpx
import pytest

from kebap_ai.chatbot import (
    ChatbotClient,
    ChatbotConfigError,
    ChatbotResponseError,
    HuggingFaceChatbotClient,
)
from kebap_ai.config import Settings


def _mock_client(handler) -> httpx.Client:
    return httpx.Client(transport=httpx.MockTransport(handler))


@pytest.mark.unit
def test_missing_api_key_raises(make_settings) -> None:
    with pytest.raises(ChatbotConfigError, match="ANTHROPIC_API_KEY"):
        ChatbotClient(make_settings())


@pytest.mark.unit
def test_settings_load_dotenv_values(tmp_path, monkeypatch) -> None:
    env_file = tmp_path / ".env"
    local_env_file = tmp_path / ".env.local"
    env_file.write_text(
        "ANTHROPIC_API_URL=https://api.anthropic.test/v1/messages\n"
        "ANTHROPIC_API_KEY=env-test-key\n"
        "CLAUDE_MODEL=claude-test-model\n"
        "CHATBOT_TIMEOUT=12\n",
        encoding="utf-8",
    )
    local_env_file.write_text(
        "ANTHROPIC_API_KEY=local-test-key\n"
        "CHATBOT_TIMEOUT=20\n",
        encoding="utf-8",
    )
    monkeypatch.delenv("ANTHROPIC_API_URL", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("CLAUDE_MODEL", raising=False)
    monkeypatch.delenv("CHATBOT_TIMEOUT", raising=False)

    settings = Settings(_env_file=env_file)

    assert settings.anthropic_api_url == "https://api.anthropic.test/v1/messages"
    assert settings.anthropic_api_key == "local-test-key"
    assert settings.claude_model == "claude-test-model"
    assert settings.chatbot_timeout == 20


@pytest.mark.unit
def test_post_body_and_anthropic_headers(make_settings) -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        captured["key"] = request.headers.get("x-api-key")
        captured["version"] = request.headers.get("anthropic-version")
        return httpx.Response(
            200,
            json={
                "content": [{"type": "text", "text": "A tasty idea."}],
                "model": "claude-test-model",
            },
        )

    settings = make_settings(
        anthropic_api_url="https://api.anthropic.test/v1/messages",
        anthropic_api_key="test-key",
        claude_model="claude-test-model",
    )
    with ChatbotClient(settings, client=_mock_client(handler)) as bot:
        assert bot.ask_text("merhaba") == "A tasty idea."

    assert captured["body"] == {
        "model": "claude-test-model",
        "max_tokens": 1024,
        "messages": [{"role": "user", "content": "merhaba"}],
    }
    assert captured["key"] == "test-key"
    assert captured["version"] == "2023-06-01"


@pytest.mark.unit
def test_missing_response_text_raises(make_settings) -> None:
    handler = lambda request: httpx.Response(200, json={"content": []})
    settings = make_settings(anthropic_api_key="test-key")
    with ChatbotClient(settings, client=_mock_client(handler)) as bot:
        with pytest.raises(ChatbotResponseError, match="did not contain text"):
            bot.ask_text("message")


@pytest.mark.unit
def test_huggingface_post_body_and_bearer_header(make_settings) -> None:
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["body"] = json.loads(request.content)
        captured["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json={"output": "A tasty idea."})

    settings = make_settings(
        hf_chatbot_url="https://chatbot.test/chat",
        hf_token="test-token",
    )
    with HuggingFaceChatbotClient(settings, client=_mock_client(handler)) as bot:
        assert bot.ask("merhaba") == {"output": "A tasty idea."}

    assert captured == {
        "body": {"input": "merhaba"},
        "auth": "Bearer test-token",
    }


@pytest.mark.integration
def test_live_chatbot_connection() -> None:
    settings = Settings(_env_file=".env")
    if not settings.anthropic_api_key:
        pytest.skip("ANTHROPIC_API_KEY tanimli degil")

    with ChatbotClient(settings) as bot:
        response = bot.send(settings.chatbot_test_message)

    print(f"\nChatbot HTTP status: {response.status_code}")
    assert response.status_code == httpx.codes.OK


@pytest.mark.integration
def test_live_huggingface_chatbot_connection() -> None:
    settings = Settings(_env_file=".env")
    if not settings.hf_chatbot_url:
        pytest.skip("HF_CHATBOT_URL tanimli degil")

    with HuggingFaceChatbotClient(settings) as bot:
        response = bot.send(settings.chatbot_test_message)

    print(f"\nHugging Face chatbot HTTP status: {response.status_code}")
    assert response.status_code == httpx.codes.OK
