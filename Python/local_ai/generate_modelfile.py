#!/usr/bin/env python3
"""Generate an Ollama Modelfile from CLI options."""

import argparse
from pathlib import Path


def build_modelfile(base_model: str, system: str | None, parameters: list[str]) -> str:
    lines = [f"FROM {base_model}"]
    for parameter in parameters:
        lines.append(f"PARAMETER {parameter}")
    if system:
        lines.extend(["SYSTEM \"\"\"", system, "\"\"\""])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate an Ollama Modelfile.")
    parser.add_argument("--from", dest="base_model", required=True, help="Base model name or GGUF path")
    parser.add_argument("--system", help="System prompt text")
    parser.add_argument(
        "--parameter",
        action="append",
        default=[],
        help="Ollama parameter, such as 'temperature 0.2'. Repeatable.",
    )
    parser.add_argument("--output", default="Modelfile", help="Output file path")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    content = build_modelfile(args.base_model, args.system, args.parameter)
    output = Path(args.output)
    output.write_text(content, encoding="utf-8")
    print(f"Wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
