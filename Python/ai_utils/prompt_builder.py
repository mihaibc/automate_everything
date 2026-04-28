#!/usr/bin/env python3
"""Build structured LLM prompts from text templates with variable substitution."""

import argparse
import json
import re
import sys
from pathlib import Path


def load_template(source: str) -> str:
    """Load template from a file path or return the raw string."""
    path = Path(source)
    if path.exists():
        return path.read_text(encoding="utf-8")
    return source


def apply_vars(template: str, vars_list: list[str]) -> str:
    """Replace {key} placeholders using key=value pairs from vars_list."""
    replacements = {}
    for entry in vars_list:
        if "=" not in entry:
            print(f"Warning: skipping malformed var '{entry}' (expected key=value)", file=sys.stderr)
            continue
        key, _, value = entry.partition("=")
        replacements[key.strip()] = value

    missing = set(re.findall(r"\{(\w+)\}", template)) - set(replacements.keys())
    if missing:
        print(f"Warning: unresolved placeholders: {', '.join(sorted(missing))}", file=sys.stderr)

    for key, value in replacements.items():
        template = template.replace(f"{{{key}}}", value)

    return template


def build_prompt(
    system: str | None,
    user: str,
    assistant_prefix: str | None = None,
    model: str = "llama3",
) -> dict:
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": user})
    if assistant_prefix:
        messages.append({"role": "assistant", "content": assistant_prefix})

    return {"model": model, "messages": messages}


def main():
    parser = argparse.ArgumentParser(
        description="Build structured LLM prompts from templates.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # From inline strings
  python prompt_builder.py --user "Summarize {topic} in 3 bullets" --vars topic=Docker

  # From template files
  python prompt_builder.py --system system.txt --user user.txt --vars name=Alice role=engineer

  # Pipe the output to a curl call
  python prompt_builder.py --user "Hello!" | curl -s http://localhost:11434/api/chat -d @-""",
    )
    parser.add_argument("--system", help="System prompt: file path or inline string")
    parser.add_argument("--user", required=True, help="User prompt: file path or inline string")
    parser.add_argument(
        "--vars",
        nargs="*",
        default=[],
        metavar="KEY=VALUE",
        help="Variable substitutions for {placeholders} in templates",
    )
    parser.add_argument("--model", default="llama3", help="Model name to embed in output (default: llama3)")
    parser.add_argument(
        "--assistant-prefix", help="Optional partial assistant response to append (for prefill)"
    )
    parser.add_argument("--indent", type=int, default=2, help="JSON indent level (default: 2, 0 = compact)")
    args = parser.parse_args()

    system_text = None
    if args.system:
        system_text = apply_vars(load_template(args.system), args.vars)

    user_text = apply_vars(load_template(args.user), args.vars)

    prompt = build_prompt(
        system=system_text,
        user=user_text,
        assistant_prefix=args.assistant_prefix,
        model=args.model,
    )

    indent = args.indent if args.indent > 0 else None
    print(json.dumps(prompt, indent=indent, ensure_ascii=False))


if __name__ == "__main__":
    main()
