import json

import pytest
from deepeval import assert_test
from deepeval.metrics import AnswerRelevancyMetric
from deepeval.models import AnthropicModel
from deepeval.test_case import LLMTestCase

from kebap_ai.chatbot import ChatbotClient, HuggingFaceChatbotClient
from kebap_ai.config import Settings


def _response_text(response) -> str:
    if isinstance(response, str):
        return response
    if isinstance(response, dict):
        content = response.get("content")
        if isinstance(content, list):
            text = "\n".join(
                block["text"]
                for block in content
                if isinstance(block, dict)
                and block.get("type") == "text"
                and isinstance(block.get("text"), str)
            ).strip()
            if text:
                return text
        for key in ("output", "response", "text", "answer"):
            value = response.get(key)
            if isinstance(value, str) and value.strip():
                return value
    return json.dumps(response, ensure_ascii=False)


@pytest.mark.integration
def test_chatbot_answer_relevance() -> None:
    settings = Settings(_env_file=".env")
    missing = [
        name
        for name, value in (
            ("ANTHROPIC_API_KEY", settings.anthropic_api_key),
        )
        if not value
    ]
    if missing:
        pytest.skip(f"Missing required evaluation settings: {', '.join(missing)}")

    with ChatbotClient(settings) as chatbot:
        answer = _response_text(chatbot.ask(settings.chatbot_test_message))

    metric = AnswerRelevancyMetric(
        threshold=settings.chatbot_eval_threshold,
        model=AnthropicModel(
            model=settings.claude_model,
            api_key=settings.anthropic_api_key,
        ),
        include_reason=True,
    )
    assert_test(
        LLMTestCase(
            input=settings.chatbot_test_message,
            actual_output=answer,
        ),
        [metric],
    )


@pytest.mark.integration
def test_huggingface_chatbot_answer_relevance() -> None:
    settings = Settings(_env_file=".env")
    missing = [
        name
        for name, value in (
            ("HF_CHATBOT_URL", settings.hf_chatbot_url),
            ("HF_TOKEN", settings.hf_token),
            ("ANTHROPIC_API_KEY", settings.anthropic_api_key),
        )
        if not value
    ]
    if missing:
        pytest.skip(f"Missing required evaluation settings: {', '.join(missing)}")

    with HuggingFaceChatbotClient(settings) as chatbot:
        answer = _response_text(chatbot.ask(settings.chatbot_test_message))

    metric = AnswerRelevancyMetric(
        threshold=settings.chatbot_eval_threshold,
        model=AnthropicModel(
            model=settings.claude_model,
            api_key=settings.anthropic_api_key,
        ),
        include_reason=True,
    )
    assert_test(
        LLMTestCase(
            input=settings.chatbot_test_message,
            actual_output=answer,
        ),
        [metric],
    )
