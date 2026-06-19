#!/usr/bin/env python3
"""Print a compact report of models installed in Ollama."""

import argparse
import json
import sys
from urllib.error import HTTPError, URLError
from urllib.request import urlopen


def fetch_models(host: str, timeout: int) -> list[dict]:
    with urlopen(f"{host.rstrip('/')}/api/tags", timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))
    return data.get("models", [])


def format_size(size_bytes: int | None) -> str:
    if not size_bytes:
        return "unknown"
    size = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024 or unit == "TB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return "unknown"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Report installed Ollama models.")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama base URL")
    parser.add_argument("--timeout", type=int, default=10, help="Request timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Print raw model data as JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        models = fetch_models(args.host, args.timeout)
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"Error: could not reach Ollama at {args.host}: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(models, indent=2))
        return 0

    if not models:
        print("No models installed.")
        return 0

    print(f"{'Name':30} {'Size':>12}  Modified")
    print("-" * 64)
    for model in models:
        print(f"{model.get('name', 'unknown'):30} {format_size(model.get('size')):>12}  {model.get('modified_at', '')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
