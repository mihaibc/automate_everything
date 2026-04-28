#!/usr/bin/env python3
"""Run batch LLM inference against any OpenAI-compatible endpoint (Ollama, OpenAI, LM Studio)."""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests", file=sys.stderr)
    sys.exit(1)


def load_prompts(path: str) -> list[dict]:
    """Load prompts from a JSONL file. Each line must be a JSON object with a 'messages' key."""
    prompts = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError as e:
                print(f"Warning: skipping line {i} (JSON error: {e})", file=sys.stderr)
                continue
            if "messages" not in obj and "prompt" not in obj:
                print(f"Warning: line {i} has no 'messages' or 'prompt' key — skipping", file=sys.stderr)
                continue
            prompts.append({"_line": i, **obj})
    return prompts


def run_single(
    prompt: dict,
    endpoint: str,
    model: str,
    timeout: int,
    api_key: str,
) -> dict:
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {k: v for k, v in prompt.items() if not k.startswith("_")}
    if "model" not in payload:
        payload["model"] = model
    payload["stream"] = False

    url = endpoint.rstrip("/") + "/chat/completions"
    # Fall back to /api/chat for native Ollama format
    if "messages" not in payload and "prompt" in payload:
        url = endpoint.rstrip("/").replace("/v1", "") + "/api/generate"

    start = time.monotonic()
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()
        data = resp.json()
        elapsed = round(time.monotonic() - start, 3)

        # Extract content from OpenAI or Ollama response shapes
        content = None
        if "choices" in data:
            content = data["choices"][0]["message"]["content"]
        elif "message" in data:
            content = data["message"]["content"]
        elif "response" in data:
            content = data["response"]

        return {
            "_line": prompt["_line"],
            "input": payload,
            "output": content,
            "elapsed_s": elapsed,
            "status": "ok",
        }
    except Exception as e:
        return {
            "_line": prompt["_line"],
            "input": payload,
            "output": None,
            "elapsed_s": round(time.monotonic() - start, 3),
            "status": "error",
            "error": str(e),
        }


def main():
    parser = argparse.ArgumentParser(
        description="Batch LLM inference against any OpenAI-compatible endpoint.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Input JSONL format (one JSON object per line):
  {"messages": [{"role": "user", "content": "What is Docker?"}]}
  {"model": "mistral", "messages": [{"role": "user", "content": "Explain Git in one line."}]}

Examples:
  python batch_inference.py --input prompts.jsonl --output results.jsonl
  python batch_inference.py --input prompts.jsonl --endpoint https://api.openai.com/v1 --model gpt-4o --api-key $OPENAI_API_KEY
  python batch_inference.py --input prompts.jsonl --workers 8 --timeout 120""",
    )
    parser.add_argument("--input", required=True, help="Input JSONL file with prompts")
    parser.add_argument("--output", default="results.jsonl", help="Output JSONL file (default: results.jsonl)")
    parser.add_argument(
        "--endpoint",
        default="http://localhost:11434/v1",
        help="OpenAI-compatible API base URL (default: http://localhost:11434/v1)",
    )
    parser.add_argument("--model", default="llama3", help="Default model (default: llama3)")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers (default: 4)")
    parser.add_argument("--timeout", type=int, default=60, help="Per-request timeout in seconds (default: 60)")
    parser.add_argument("--api-key", default="", help="API key (optional, for OpenAI etc.)")
    args = parser.parse_args()

    prompts = load_prompts(args.input)
    if not prompts:
        print("No valid prompts found in input file.", file=sys.stderr)
        sys.exit(1)

    print(f"Loaded {len(prompts)} prompts. Running with {args.workers} workers...", file=sys.stderr)

    results = [None] * len(prompts)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_single, p, args.endpoint, args.model, args.timeout, args.api_key): i
            for i, p in enumerate(prompts)
        }
        completed = 0
        for future in as_completed(futures):
            idx = futures[future]
            results[idx] = future.result()
            completed += 1
            status = results[idx]["status"]
            line = results[idx]["_line"]
            elapsed = results[idx]["elapsed_s"]
            print(
                f"  [{completed}/{len(prompts)}] line {line} — {status} ({elapsed}s)",
                file=sys.stderr,
            )

    out_path = Path(args.output)
    ok = sum(1 for r in results if r["status"] == "ok")
    errors = len(results) - ok

    with open(out_path, "w", encoding="utf-8") as f:
        for result in results:
            f.write(json.dumps(result, ensure_ascii=False) + "\n")

    print(f"\nDone. {ok} ok, {errors} errors. Output: {out_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
