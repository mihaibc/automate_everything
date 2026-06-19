#!/usr/bin/env python3
"""Benchmark a local Ollama chat model with repeated prompts."""

import argparse
import json
import statistics
import sys
import time
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


def post_json(url: str, payload: dict, timeout: int) -> dict:
    data = json.dumps(payload).encode("utf-8")
    request = Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def run_once(host: str, model: str, prompt: str, timeout: int) -> dict:
    payload = {
        "model": model,
        "stream": False,
        "messages": [{"role": "user", "content": prompt}],
    }
    start = time.monotonic()
    response = post_json(f"{host.rstrip('/')}/api/chat", payload, timeout)
    elapsed = time.monotonic() - start
    content = response.get("message", {}).get("content", "")
    eval_count = response.get("eval_count") or 0
    tokens_per_second = eval_count / elapsed if eval_count else None
    return {
        "elapsed_s": round(elapsed, 3),
        "eval_count": eval_count,
        "tokens_per_second": round(tokens_per_second, 2) if tokens_per_second else None,
        "chars": len(content),
    }


def summarize(results: list[dict]) -> dict:
    elapsed = [item["elapsed_s"] for item in results]
    tps = [item["tokens_per_second"] for item in results if item["tokens_per_second"] is not None]
    return {
        "runs": len(results),
        "elapsed_min_s": min(elapsed),
        "elapsed_median_s": round(statistics.median(elapsed), 3),
        "elapsed_max_s": max(elapsed),
        "tokens_per_second_median": round(statistics.median(tps), 2) if tps else None,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Benchmark a local Ollama chat model.")
    parser.add_argument("--host", default="http://localhost:11434", help="Ollama base URL")
    parser.add_argument("--model", default="llama3", help="Model to benchmark")
    parser.add_argument("--prompt", default="Explain local LLM inference in one paragraph.", help="Prompt to run")
    parser.add_argument("--runs", type=int, default=3, help="Number of benchmark runs")
    parser.add_argument("--timeout", type=int, default=120, help="Per-request timeout in seconds")
    parser.add_argument("--json", action="store_true", help="Print machine-readable JSON")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.runs < 1:
        print("Error: --runs must be >= 1", file=sys.stderr)
        return 1

    results = []
    try:
        for run_number in range(1, args.runs + 1):
            result = run_once(args.host, args.model, args.prompt, args.timeout)
            results.append(result)
            if not args.json:
                print(f"Run {run_number}: {result}")
    except (HTTPError, URLError, TimeoutError) as exc:
        print(f"Error: request failed: {exc}", file=sys.stderr)
        return 1

    output = {"model": args.model, "summary": summarize(results), "runs": results}
    if args.json:
        print(json.dumps(output, indent=2))
    else:
        print("\nSummary")
        for key, value in output["summary"].items():
            print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
