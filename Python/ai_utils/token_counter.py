#!/usr/bin/env python3
"""Count tokens in text for various LLM models using tiktoken."""

import argparse
import sys

MODEL_ENCODINGS = {
    "gpt-4": "cl100k_base",
    "gpt-4o": "o200k_base",
    "gpt-3.5-turbo": "cl100k_base",
    "text-davinci-003": "p50k_base",
    "cl100k_base": "cl100k_base",
    "o200k_base": "o200k_base",
    "p50k_base": "p50k_base",
}


def count_tokens(text: str, model: str) -> int:
    try:
        import tiktoken
    except ImportError:
        print("Error: tiktoken not installed. Run: pip install tiktoken", file=sys.stderr)
        sys.exit(1)

    encoding_name = MODEL_ENCODINGS.get(model, model)
    try:
        enc = tiktoken.get_encoding(encoding_name)
    except Exception:
        try:
            enc = tiktoken.encoding_for_model(model)
        except Exception:
            print(f"Error: unknown model or encoding '{model}'", file=sys.stderr)
            print(f"Known models: {', '.join(MODEL_ENCODINGS.keys())}", file=sys.stderr)
            sys.exit(1)

    return len(enc.encode(text))


def main():
    parser = argparse.ArgumentParser(
        description="Count tokens in text for LLM models.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python token_counter.py --text "Hello, world!" --model gpt-4
  echo "Hello, world!" | python token_counter.py --model gpt-3.5-turbo
  python token_counter.py --text "Some text" --model cl100k_base --verbose""",
    )
    parser.add_argument("--text", help="Text to count tokens for (or pipe via stdin)")
    parser.add_argument(
        "--model",
        default="gpt-4",
        help=f"Model or encoding name (default: gpt-4). Options: {', '.join(MODEL_ENCODINGS.keys())}",
    )
    parser.add_argument(
        "--verbose", action="store_true", help="Show model and character count alongside token count"
    )
    args = parser.parse_args()

    if args.text:
        text = args.text
    elif not sys.stdin.isatty():
        text = sys.stdin.read().rstrip("\n")
    else:
        parser.print_help()
        sys.exit(1)

    token_count = count_tokens(text, args.model)

    if args.verbose:
        print(f"Model   : {args.model}")
        print(f"Chars   : {len(text)}")
        print(f"Tokens  : {token_count}")
    else:
        print(token_count)


if __name__ == "__main__":
    main()
