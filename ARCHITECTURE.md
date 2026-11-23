# Architecture

`prompt-enhance.py` is a single-process CLI. It loads a system prompt from markdown, reads a user prompt from argv or stdin, and calls OpenAI Chat Completions.

```
argv / stdin ──► argparse
                     │
                     ├─ prompt
                     ├─ --silent
                     └─ --model ──► PROMPT_ENHANCE_MODEL ──► gpt-6.2-astra
                                        │
instructions.md ◄── PROMPT_ENHANCE_INSTRUCTIONS
                     │
                     ▼
            openai.chat.completions.create
                     │
                     ▼
              stdout (polished prompt)
```

## Runtime config

| Setting | Resolution |
| --- | --- |
| Model | `--model` → `PROMPT_ENHANCE_MODEL` → `DEFAULT_MODEL` (`gpt-6.2-astra`) |
| Instructions file | `PROMPT_ENHANCE_INSTRUCTIONS` → `instructions.md` beside the script |
| API key | `OPENAI_API_KEY` (required) |
| Timeout | `TIMEOUT` constant (30s) |

## API constraints

The default model is a GPT-6.2 reasoning model. The Chat Completions request sends only `model`, `timeout`, and `messages`. It does not send `temperature`, `top_p`, `logprobs`, `top_logprobs`, or `max_tokens`, which those models reject. `max_completion_tokens` is the supported output cap if one is added later.

Silent mode skips the Halo spinner so stdout stays pipe-clean.
