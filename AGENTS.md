# AGENTS.md

## Project

CLI tool that polishes software-development prompts via OpenAI Chat Completions.

## Layout

- `prompt-enhance.py` — CLI entrypoint (`uv run prompt-enhance.py …`)
- `instructions.md` — system prompt loaded at runtime
- `README.md` — usage and configuration

## Conventions

- Bind no HTTP server; this is a one-shot CLI.
- Do not commit secrets. Never read or write `.env`; use `.env.example` if env docs are needed.
- Default model is OpenAI's current flagship chat/text model from https://developers.openai.com/api/docs/models. Confirm Chat Completions support before changing it.
- Model resolution: `--model` > `PROMPT_ENHANCE_MODEL` > `DEFAULT_MODEL`.
- Instructions path: `PROMPT_ENHANCE_INSTRUCTIONS` > `instructions.md` next to the script.
- Newer flagship models reject `temperature`, `top_p`, `logprobs`, `top_logprobs`, and `max_tokens`. Keep those omitted; use `max_completion_tokens` if a cap is required.
- Keep silent mode (`-s` / `--silent`), Halo spinner, and `TIMEOUT`.

## Verify

```bash
python3 -m py_compile prompt-enhance.py
python3 prompt-enhance.py --help
```

A live API call needs `OPENAI_API_KEY`. If it is unset, do not claim a live test.

## Progress

- 2026-11-23: Default model `gpt-4o` → `gpt-6.2-astra`; added `--model` / `PROMPT_ENHANCE_MODEL`; instructions path is script-adjacent with `PROMPT_ENHANCE_INSTRUCTIONS` override; Chat Completions call omits parameters rejected by GPT-6.2.
