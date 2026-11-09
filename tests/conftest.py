import pytest

from kebap_ai.config import Settings


@pytest.fixture
def make_settings(monkeypatch: pytest.MonkeyPatch):
    def factory(**overrides) -> Settings:
        monkeypatch.delenv("ANTHROPIC_API_URL", raising=False)
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        monkeypatch.delenv("CLAUDE_MODEL", raising=False)
        monkeypatch.delenv("HF_CHATBOT_URL", raising=False)
        monkeypatch.delenv("HF_TOKEN", raising=False)
        monkeypatch.delenv("CHATBOT_INPUT_KEY", raising=False)
        return Settings(_env_file=None, **overrides)

    return factory
