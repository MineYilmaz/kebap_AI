# Kebab AI

This project is a minimal Flask starter app for a small AI-style kitchen idea generator.

## Getting started

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if it is not already installed.
2. Create the environment and install dependencies:
   ```bash
   uv sync --group dev
   ```
3. Copy `.env.example` to `.env` and adjust settings as needed.
4. Run the tests:
   ```bash
   uv run pytest
   ```
   Chatbot tests that use an HTTP mock only:
   ```bash
   uv run pytest -m unit
   ```
   Live Claude API check (requires `ANTHROPIC_API_KEY` in `.env`):
   ```bash
   uv run pytest -m integration -s
   ```
   Hugging Face chatbot evaluation (requires `HF_CHATBOT_URL`, `HF_TOKEN` in
   `.env` / `.env.local`, and `ANTHROPIC_API_KEY` for the evaluation judge):
   ```bash
   uv run deepeval test run tests/evals/test_chatbot_quality.py::test_huggingface_chatbot_answer_relevance -m integration
   ```
5. Add your Claude API key to `ANTHROPIC_API_KEY` in `.env`. To connect
   DeepEval with Confident AI, paste your API key into the empty
   `CONFIDENT_AI_API_KEY=` entry in `.env.local`, then run:
   ```powershell
   $env:CONFIDENT_AI_API_KEY = ((Get-Content .env.local | Where-Object { $_ -match '^CONFIDENT_AI_API_KEY=' } | Select-Object -First 1) -replace '^CONFIDENT_AI_API_KEY=', '').Trim()
   if (-not $env:CONFIDENT_AI_API_KEY) { throw "Add the key to .env.local first." }
   try { uv run deepeval login --api-key $env:CONFIDENT_AI_API_KEY } finally { Remove-Item Env:CONFIDENT_AI_API_KEY -ErrorAction SilentlyContinue }
   ```
   DeepEval chatbot evaluations can then be run with
   `uv run deepeval test run tests/evals -m integration`. They need
   `ANTHROPIC_API_KEY` configured. The Hugging Face evaluation also needs
   `HF_CHATBOT_URL` and `HF_TOKEN`.
6. Start the app:
   ```bash
   uv run python app.py
   ```
7. Open the host and port configured in `.env` (defaults to http://127.0.0.1:8000).

See [Instructions.md](Instructions.md) for configuration, debugging, and Git details.

## Available endpoints

- GET /
- GET /api/health
- POST /api/generate

The Claude client in `kebap_ai/chatbot.py` uses Anthropic's Messages API.
Its unit tests use `httpx.MockTransport` and make no network requests.

## Notes

This is intentionally lightweight so it can serve as a starting point for a bigger AI project.
