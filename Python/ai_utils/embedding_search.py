#!/usr/bin/env python3
"""Semantic search over a folder of text files using local sentence-transformers embeddings."""

import argparse
import json
import math
import sys
from pathlib import Path

INDEX_FILE = "embedding_index.json"
DEFAULT_MODEL = "all-MiniLM-L6-v2"


def get_model(model_name: str):
    try:
        from sentence_transformers import SentenceTransformer
    except ImportError:
        print(
            "Error: sentence-transformers not installed. Run: pip install sentence-transformers",
            file=sys.stderr,
        )
        sys.exit(1)
    return SentenceTransformer(model_name)


def normalize(vec: list[float]) -> list[float]:
    norm = math.sqrt(sum(x * x for x in vec))
    if norm == 0:
        return vec
    return [x / norm for x in vec]


def cosine(a: list[float], b: list[float]) -> float:
    return sum(x * y for x, y in zip(a, b, strict=False))


def cmd_index(args):
    doc_dir = Path(args.dir)
    if not doc_dir.is_dir():
        print(f"Error: '{doc_dir}' is not a directory", file=sys.stderr)
        sys.exit(1)

    files = list(doc_dir.rglob("*.txt"))
    if not files:
        print(f"No .txt files found in '{doc_dir}'", file=sys.stderr)
        sys.exit(1)

    print(f"Indexing {len(files)} files with model '{args.model}'...", file=sys.stderr)
    model = get_model(args.model)

    texts = [f.read_text(encoding="utf-8", errors="replace") for f in files]
    paths = [str(f) for f in files]
    raw_embeddings = model.encode(texts, show_progress_bar=True)

    index = {
        "model": args.model,
        "documents": [
            {"path": path, "embedding": normalize(emb.tolist())}
            for path, emb in zip(paths, raw_embeddings, strict=True)
        ],
    }

    out_path = Path(args.output)
    out_path.write_text(json.dumps(index, ensure_ascii=False), encoding="utf-8")
    print(f"Index saved to '{out_path}' ({len(files)} documents).", file=sys.stderr)


def cmd_search(args):
    index_path = Path(args.index)
    if not index_path.exists():
        print(f"Error: index file '{index_path}' not found. Run 'index' first.", file=sys.stderr)
        sys.exit(1)

    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, KeyError):
        print("Error: index file is corrupt or invalid. Re-run 'index' to rebuild.", file=sys.stderr)
        sys.exit(1)

    stored_model = index["model"]
    documents = index["documents"]

    model_name = args.model or stored_model
    if args.model and args.model != stored_model:
        print(
            f"Warning: search model '{args.model}' differs from index model '{stored_model}'. "
            "Results may be inaccurate. Re-index with the same model to fix this.",
            file=sys.stderr,
        )
    model = get_model(model_name)

    raw_query = model.encode([args.query])[0]
    query_vec = normalize(raw_query.tolist())

    scored = [
        {"score": cosine(query_vec, doc["embedding"]), "file": doc["path"]}
        for doc in documents
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)

    top_n = min(args.top, len(scored))
    results = [
        {"rank": i + 1, "score": round(r["score"], 4), "file": r["file"]}
        for i, r in enumerate(scored[:top_n])
    ]

    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(f'\nTop {top_n} results for: "{args.query}"\n')
        for r in results:
            print(f"  {r['rank']}. [{r['score']:.4f}]  {r['file']}")


def main():
    parser = argparse.ArgumentParser(
        description="Semantic search over text files using local embeddings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  # Index a directory of .txt files
  python embedding_search.py index --dir ./docs

  # Search the index
  python embedding_search.py search --query "how to deploy with Docker"

  # Search with custom top-N and JSON output
  python embedding_search.py search --query "authentication flow" --top 10 --json

  # Use a different model
  python embedding_search.py index --dir ./docs --model all-mpnet-base-v2""",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    idx_p = sub.add_parser("index", help="Build an embedding index from a directory of .txt files")
    idx_p.add_argument("--dir", required=True, help="Directory containing .txt files to index")
    idx_p.add_argument("--output", default=INDEX_FILE, help=f"Output index file (default: {INDEX_FILE})")
    idx_p.add_argument(
        "--model",
        default=DEFAULT_MODEL,
        help=f"Sentence-transformers model (default: {DEFAULT_MODEL})",
    )

    srch_p = sub.add_parser("search", help="Search the index with a natural language query")
    srch_p.add_argument("--query", required=True, help="Search query")
    srch_p.add_argument("--index", default=INDEX_FILE, help=f"Index file to search (default: {INDEX_FILE})")
    srch_p.add_argument("--top", type=int, default=5, help="Number of results to return (default: 5)")
    srch_p.add_argument("--model", default=None, help="Override the model used at index time")
    srch_p.add_argument("--json", action="store_true", help="Output results as JSON")

    args = parser.parse_args()

    if args.command == "index":
        cmd_index(args)
    elif args.command == "search":
        cmd_search(args)


if __name__ == "__main__":
    main()
