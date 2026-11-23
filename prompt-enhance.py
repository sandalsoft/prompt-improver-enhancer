#!/usr/bin/env python3
# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "openai>=1.0.0",
#     "halo>=0.0.31",
# ]
# ///
"""
polish_prompt.py
Refines a raw software-development prompt using the
"Code-Prompt Polisher" system prompt.

USAGE EXAMPLES
--------------
  uv run prompt-enhance.py "Need help sorting a list faster in JS"
  uv run prompt-enhance.py --prompt "Need help sorting a list faster in JS"
  uv run prompt-enhance.py --model gpt-6.2-sol "Need help sorting a list faster in JS"
  echo "Need help sorting a list faster in JS" | uv run prompt-enhance.py
  cat myprompt.txt | uv run prompt-enhance.py
"""
import os
import sys
import argparse
import openai
from halo import Halo

# ─────────────────── Configuration ─────────────────── #
# Flagship chat/text model from OpenAI's models catalog:
# https://developers.openai.com/api/docs/models
DEFAULT_MODEL = "gpt-6.2-astra"
TIMEOUT = 30              # Seconds
# ────────────────────────────────────────────────────── #


def default_instructions_path() -> str:
    """instructions.md next to this script."""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "instructions.md")


def resolve_instructions_path() -> str:
    """PROMPT_ENHANCE_INSTRUCTIONS, then the script-adjacent default."""
    env_path = os.getenv("PROMPT_ENHANCE_INSTRUCTIONS", "").strip()
    return env_path or default_instructions_path()


def resolve_model(cli_model):
    """`--model`, then PROMPT_ENHANCE_MODEL, then DEFAULT_MODEL."""
    if cli_model and cli_model.strip():
        return cli_model.strip()
    env_model = os.getenv("PROMPT_ENHANCE_MODEL", "").strip()
    return env_model or DEFAULT_MODEL


def load_system_prompt(path=None) -> str:
    """Load the system prompt from instructions.md file."""
    instructions_file = path or resolve_instructions_path()
    try:
        with open(instructions_file, "r", encoding="utf-8") as f:
            content = f.read().strip()
            # Remove the markdown header if present
            if content.startswith("# Instructions\n"):
                content = content[len("# Instructions\n"):].strip()
            return content
    except FileNotFoundError:
        sys.stderr.write(
            f"Error: instructions file not found: {instructions_file}\n")
        sys.exit(1)
    except Exception as e:
        sys.stderr.write(f"Error reading {instructions_file}: {e}\n")
        sys.exit(1)


def read_stdin() -> str:
    """Read a prompt from STDIN; exit if nothing was piped in."""
    data = sys.stdin.read().strip()
    if not data:
        sys.stderr.write(
            "No input detected. Pipe or redirect a prompt into stdin.\n")
        sys.exit(1)
    return data


def get_prompt():
    """Get prompt, silent flag, and model from CLI, env, or stdin."""
    parser = argparse.ArgumentParser(
        description="Refine a raw software-development prompt using the Code-Prompt Polisher system.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
USAGE EXAMPLES:
  echo "Need help sorting a list faster in JS" | python polish_prompt.py
  cat myprompt.txt | python polish_prompt.py
  python polish_prompt.py "Need help sorting a list faster in JS"
  python polish_prompt.py --prompt "Need help sorting a list faster in JS"
  python polish_prompt.py --model gpt-6.2-sol "Need help sorting a list faster in JS"
  python polish_prompt.py -s "Need help sorting a list faster in JS" > output.txt
        """.strip()
    )
    parser.add_argument(
        "prompt",
        nargs="?",
        help="The prompt to polish (if not provided, reads from stdin)"
    )
    parser.add_argument(
        "--prompt",
        dest="prompt_flag",
        help="The prompt to polish (alternative to positional argument)"
    )
    parser.add_argument(
        "--model",
        metavar="MODEL",
        help=(
            "OpenAI chat model. Precedence: this flag, then "
            f"PROMPT_ENHANCE_MODEL, then {DEFAULT_MODEL}."
        ),
    )
    parser.add_argument(
        "-s", "--silent",
        action="store_true",
        help="Silent mode - disable spinner for clean output that can be piped"
    )

    args = parser.parse_args()

    # Priority: --prompt flag > positional argument > stdin
    if args.prompt_flag:
        prompt = args.prompt_flag.strip()
    elif args.prompt:
        prompt = args.prompt.strip()
    else:
        # Fall back to stdin if no arguments provided
        if sys.stdin.isatty():
            parser.error(
                "No prompt provided. Either pass as argument or pipe to stdin.")
        prompt = read_stdin()

    return prompt, args.silent, resolve_model(args.model)


def enhance_prompt(raw_prompt, system_prompt, model):
    """Call Chat Completions with params compatible with current flagship models."""
    # gpt-6.2-* reasoning models reject temperature, top_p, logprobs,
    # top_logprobs, and max_tokens. Omit them; use max_completion_tokens
    # only if a caller later needs an output cap.
    return openai.chat.completions.create(
        model=model,
        timeout=TIMEOUT,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": raw_prompt},
        ],
    )


def main() -> None:
    raw_prompt, silent_mode, model = get_prompt()
    system_prompt = load_system_prompt()

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        sys.stderr.write(
            "Error: OPENAI_API_KEY environment variable not set.\n")
        sys.exit(1)

    openai.api_key = api_key

    if not silent_mode:
        spinner = Halo(text="Refining prompt...", spinner="dots")
        spinner.start()

    response = enhance_prompt(raw_prompt, system_prompt, model)

    if not silent_mode:
        spinner.stop()

    print(response.choices[0].message.content.strip())


if __name__ == "__main__":
    main()
