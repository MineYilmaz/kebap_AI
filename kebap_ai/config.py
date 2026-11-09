import os
from pathlib import Path

from dotenv import dotenv_values


class Settings:
    def __init__(
        self,
        _env_file: str | Path | None = ".env",
        *,
        anthropic_api_url: str | None = None,
        anthropic_api_key: str | None = None,
        claude_model: str | None = None,
        hf_chatbot_url: str | None = None,
        hf_token: str | None = None,
        chatbot_input_key: str | None = None,
        chatbot_timeout: float | None = None,
        chatbot_test_message: str | None = None,
        chatbot_eval_threshold: float | None = None,
    ) -> None:
        file_values = dotenv_values(_env_file) if _env_file is not None else {}
        if _env_file is not None:
            local_env_file = Path(_env_file).with_name(".env.local")
            if local_env_file != Path(_env_file):
                file_values.update(dotenv_values(local_env_file))

        def setting(name: str, explicit: str | None, default: str = "") -> str:
            if explicit is not None:
                return explicit
            return os.getenv(name, file_values.get(name) or default)

        self.anthropic_api_url = setting(
            "ANTHROPIC_API_URL",
            anthropic_api_url,
            "https://api.anthropic.com/v1/messages",
        ).strip()
        self.anthropic_api_key = setting(
            "ANTHROPIC_API_KEY", anthropic_api_key
        ).strip()
        self.claude_model = setting(
            "CLAUDE_MODEL", claude_model, "claude-sonnet-4-5"
        ).strip()
        self.hf_chatbot_url = setting("HF_CHATBOT_URL", hf_chatbot_url).strip()
        self.hf_token = setting("HF_TOKEN", hf_token).strip()
        self.chatbot_input_key = setting(
            "CHATBOT_INPUT_KEY", chatbot_input_key, "input"
        ).strip()
        timeout = (
            str(chatbot_timeout)
            if chatbot_timeout is not None
            else setting("CHATBOT_TIMEOUT", None, "30")
        )
        self.chatbot_timeout = float(timeout)
        self.chatbot_test_message = setting(
            "CHATBOT_TEST_MESSAGE", chatbot_test_message, "Merhaba"
        )
        threshold = (
            str(chatbot_eval_threshold)
            if chatbot_eval_threshold is not None
            else setting("CHATBOT_EVAL_THRESHOLD", None, "0.7")
        )
        self.chatbot_eval_threshold = float(threshold)
