from app import create_app


class StubClaudeClient:
    def __init__(self, _settings, response="A bright, flavorful dish idea."):
        self.response = response

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return None

    def ask_text(self, prompt):
        self.prompt = prompt
        return self.response


def test_health_uses_configured_app_name():
    app = create_app({"TESTING": True, "APP_NAME": "test-kitchen"})
    response = app.test_client().get("/api/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "app": "test-kitchen"}


def test_generate_uses_claude_for_request_values(monkeypatch):
    monkeypatch.setattr("app.ChatbotClient", StubClaudeClient)
    app = create_app(
        {
            "TESTING": True,
            "ANTHROPIC_API_KEY": "test-key",
        }
    )
    response = app.test_client().post(
        "/api/generate", json={"dish": "Falafel", "mood": "spicy"}
    )

    assert response.status_code == 200
    assert response.get_json() == {
        "title": "Falafel AI Idea",
        "summary": "A bright, flavorful dish idea.",
        "dish": "Falafel",
        "mood": "spicy",
    }


def test_generate_uses_configured_defaults(monkeypatch):
    monkeypatch.setattr("app.ChatbotClient", StubClaudeClient)
    app = create_app(
        {
            "TESTING": True,
            "DEFAULT_DISH": "lentil",
            "DEFAULT_MOOD": "cozy",
            "ANTHROPIC_API_KEY": "test-key",
        }
    )
    response = app.test_client().post("/api/generate", json={})

    assert response.get_json() == {
        "title": "Lentil AI Idea",
        "summary": "A bright, flavorful dish idea.",
        "dish": "lentil",
        "mood": "cozy",
    }


def test_generate_returns_error_when_api_key_is_missing():
    app = create_app({"TESTING": True, "ANTHROPIC_API_KEY": ""})
    response = app.test_client().post("/api/generate", json={})

    assert response.status_code == 503
    assert response.get_json() == {"error": "ANTHROPIC_API_KEY is required"}


def test_generate_uses_defaults_for_invalid_payload_values(monkeypatch):
    monkeypatch.setattr("app.ChatbotClient", StubClaudeClient)
    app = create_app(
        {
            "TESTING": True,
            "DEFAULT_DISH": "kebab",
            "DEFAULT_MOOD": "fresh",
            "ANTHROPIC_API_KEY": "test-key",
        }
    )
    response = app.test_client().post(
        "/api/generate", json={"dish": ["invalid"], "mood": None}
    )

    result = response.get_json()
    assert result["dish"] == "kebab"
    assert result["mood"] == "fresh"
