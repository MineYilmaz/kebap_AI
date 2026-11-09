from typing import Any

import httpx

from kebap_ai.config import Settings


class ChatbotConfigError(ValueError):
    """Raised when required chatbot configuration is missing or invalid."""


class ChatbotResponseError(ValueError):
    """Raised when Claude returns an unexpected response."""


class ChatbotClient:
    def __init__(
        self, settings: Settings, client: httpx.Client | None = None
    ) -> None:
        if not settings.anthropic_api_key:
            raise ChatbotConfigError("ANTHROPIC_API_KEY is required")
        if not settings.anthropic_api_url:
            raise ChatbotConfigError("ANTHROPIC_API_URL is required")
        if not settings.claude_model:
            raise ChatbotConfigError("CLAUDE_MODEL cannot be empty")
        if settings.chatbot_timeout <= 0:
            raise ChatbotConfigError("CHATBOT_TIMEOUT must be greater than zero")

        self.settings = settings
        if client is None:
            self._client = httpx.Client(timeout=settings.chatbot_timeout)
        else:
            self._client = client

    def __enter__(self) -> "ChatbotClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def send(self, message: str) -> httpx.Response:
        headers = {
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
            "x-api-key": self.settings.anthropic_api_key,
        }
        return self._client.post(
            self.settings.anthropic_api_url,
            json={
                "model": self.settings.claude_model,
                "max_tokens": 1024,
                "messages": [{"role": "user", "content": message}],
            },
            headers=headers,
        )

    def ask(self, message: str) -> Any:
        response = self.send(message)
        response.raise_for_status()
        return response.json()

    def ask_text(self, message: str) -> str:
        response = self.ask(message)
        content = response.get("content") if isinstance(response, dict) else None
        if not isinstance(content, list):
            raise ChatbotResponseError("Claude response did not contain text")

        text = "\n".join(
            block["text"]
            for block in content
            if isinstance(block, dict)
            and block.get("type") == "text"
            and isinstance(block.get("text"), str)
        ).strip()
        if not text:
            raise ChatbotResponseError("Claude response did not contain text")
        return text


class HuggingFaceChatbotClient:
    def __init__(
        self, settings: Settings, client: httpx.Client | None = None
    ) -> None:
        if not settings.hf_chatbot_url:
            raise ChatbotConfigError("HF_CHATBOT_URL is required")
        if not settings.chatbot_input_key:
            raise ChatbotConfigError("CHATBOT_INPUT_KEY cannot be empty")
        if settings.chatbot_timeout <= 0:
            raise ChatbotConfigError("CHATBOT_TIMEOUT must be greater than zero")

        self.settings = settings
        if client is None:
            self._client = httpx.Client(timeout=settings.chatbot_timeout)
        else:
            self._client = client

    def __enter__(self) -> "HuggingFaceChatbotClient":
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    def close(self) -> None:
        self._client.close()

    def send(self, message: str) -> httpx.Response:
        headers = {}
        if self.settings.hf_token:
            headers["Authorization"] = "Bearer " + self.settings.hf_token
        return self._client.post(
            self.settings.hf_chatbot_url,
            json={self.settings.chatbot_input_key: message},
            headers=headers,
        )

    def ask(self, message: str) -> Any:
        response = self.send(message)
        response.raise_for_status()
        return response.json()
