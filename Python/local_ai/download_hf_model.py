#!/usr/bin/env python3
"""Download selected files from a Hugging Face model repository."""

import argparse
import sys
from pathlib import Path


def download_model(repo_id: str, local_dir: Path, patterns: list[str] | None, revision: str | None, dry_run: bool) -> Path:
    if dry_run:
        pattern_text = ", ".join(patterns or ["all files"])
        print(f"Would download {repo_id} ({pattern_text}) to {local_dir}")
        return local_dir

    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise RuntimeError("huggingface-hub is required. Install with: pip install huggingface-hub") from exc

    return Path(
        snapshot_download(
            repo_id=repo_id,
            local_dir=str(local_dir),
            allow_patterns=patterns,
            revision=revision,
        )
    )


def parse_patterns(value: str | None) -> list[str] | None:
    if not value:
        return None
    return [item.strip() for item in value.split(",") if item.strip()]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Download model files from Hugging Face Hub.")
    parser.add_argument("--repo-id", required=True, help="Model repository, such as TheBloke/Llama-2-7B-GGUF")
    parser.add_argument("--local-dir", default="models", help="Directory where files are stored")
    parser.add_argument("--include", help="Comma-separated allow patterns, such as '*.gguf,tokenizer.json'")
    parser.add_argument("--revision", help="Optional branch, tag, or commit")
    parser.add_argument("--dry-run", action="store_true", help="Print the planned download without network access")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        path = download_model(
            args.repo_id,
            Path(args.local_dir).expanduser(),
            parse_patterns(args.include),
            args.revision,
            args.dry_run,
        )
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Model files available at: {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
