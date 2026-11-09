import os

import httpx
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request

from kebap_ai.chatbot import (
    ChatbotClient,
    ChatbotConfigError,
    ChatbotResponseError,
)
from kebap_ai.config import Settings

load_dotenv()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        APP_NAME=os.getenv("APP_NAME", "kebap_ai"),
        DEFAULT_DISH=os.getenv("DEFAULT_DISH", "kebab"),
        DEFAULT_MOOD=os.getenv("DEFAULT_MOOD", "fresh"),
        HOST=os.getenv("HOST", "127.0.0.1"),
        PORT=int(os.getenv("PORT", "8000")),
        DEBUG=os.getenv("DEBUG", "false").strip().lower()
        in {"1", "true", "yes", "on"},
        ANTHROPIC_API_URL=os.getenv(
            "ANTHROPIC_API_URL", "https://api.anthropic.com/v1/messages"
        ),
        ANTHROPIC_API_KEY=os.getenv("ANTHROPIC_API_KEY", ""),
        CLAUDE_MODEL=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5"),
        CHATBOT_TIMEOUT=float(os.getenv("CHATBOT_TIMEOUT", "30")),
    )
    if test_config:
        app.config.update(test_config)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok", "app": app.config["APP_NAME"]})

    @app.route("/api/generate", methods=["POST"])
    def generate():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            payload = {}

        dish_value = payload.get("dish")
        mood_value = payload.get("mood")
        dish = (
            dish_value.strip()
            if isinstance(dish_value, str) and dish_value.strip()
            else app.config["DEFAULT_DISH"]
        )
        mood = (
            mood_value.strip()
            if isinstance(mood_value, str) and mood_value.strip()
            else app.config["DEFAULT_MOOD"]
        )
        prompt = (
            "Create an appetizing, practical food idea. "
            f"Main dish: {dish.lower()}. Flavor mood: {mood}. "
            "Write a concise 2-3 sentence description and return only the "
            "description, without a title or markdown."
        )
        settings = Settings(
            _env_file=None,
            anthropic_api_url=app.config["ANTHROPIC_API_URL"],
            anthropic_api_key=app.config["ANTHROPIC_API_KEY"],
            claude_model=app.config["CLAUDE_MODEL"],
            chatbot_timeout=app.config["CHATBOT_TIMEOUT"],
        )
        try:
            with ChatbotClient(settings) as claude:
                summary = claude.ask_text(prompt)
        except ChatbotConfigError as error:
            return jsonify({"error": str(error)}), 503
        except (httpx.HTTPError, ChatbotResponseError) as error:
            app.logger.warning("Claude generation failed: %s", error)
            return jsonify({"error": "Claude could not generate an idea."}), 502

        return jsonify(
            {
                "title": f"{dish.title()} AI Idea",
                "summary": summary,
                "dish": dish,
                "mood": mood,
            }
        )

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        debug=app.config["DEBUG"],
        host=app.config["HOST"],
        port=app.config["PORT"],
    )
