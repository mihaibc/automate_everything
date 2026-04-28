# Python — AI Utils

A collection of command-line utilities for working with large language models. All scripts are standalone, dependency-light, and compatible with local models via Ollama as well as cloud APIs (OpenAI, Anthropic-compatible endpoints).

---

## Setup

```bash
pip install -r requirements.txt
```

---

## Scripts

### `token_counter.py` — Count tokens before sending to an LLM

```bash
# Inline text
python token_counter.py --text "Hello, world!" --model gpt-4

# Pipe from stdin
cat document.txt | python token_counter.py --model cl100k_base

# Verbose output
python token_counter.py --text "Some long document..." --model gpt-4o --verbose
```

Supported models/encodings: `gpt-4`, `gpt-4o`, `gpt-3.5-turbo`, `cl100k_base`, `o200k_base`, `p50k_base`.

---

### `prompt_builder.py` — Build structured prompts from templates

```bash
# Inline with variable substitution
python prompt_builder.py --user "Summarize {topic} in 3 bullets" --vars topic=Docker

# From files, output piped to Ollama
python prompt_builder.py --system system.txt --user user.txt --vars name=Alice | \
  curl -s http://localhost:11434/api/chat -d @-

# Target a specific model
python prompt_builder.py --user "Hello!" --model mistral
```

Template files use `{placeholder}` syntax. Missing variables produce a warning but don't fail.

---

### `batch_inference.py` — Run many prompts in parallel

Input: a `.jsonl` file where each line is a JSON object with a `messages` key (OpenAI format).

```bash
# Against a local Ollama instance
python batch_inference.py --input prompts.jsonl --output results.jsonl

# Against OpenAI
python batch_inference.py \
  --input prompts.jsonl \
  --endpoint https://api.openai.com/v1 \
  --model gpt-4o \
  --api-key $OPENAI_API_KEY \
  --workers 8

# Example input line (prompts.jsonl):
# {"messages": [{"role": "user", "content": "What is Kubernetes?"}]}
```

Results are written as JSONL with `status`, `output`, and `elapsed_s` fields per entry.

---

### `embedding_search.py` — Semantic search over text files

```bash
# Step 1: Build an index from a directory of .txt files
python embedding_search.py index --dir ./my_docs

# Step 2: Search
python embedding_search.py search --query "how to handle authentication"

# Top 10 results as JSON
python embedding_search.py search --query "deployment pipeline" --top 10 --json
```

The index is saved as `embedding_index.json`. Uses `all-MiniLM-L6-v2` by default — fast, runs entirely locally. No internet connection needed after the initial model download.

---

## Dependencies

| Package | Used by |
|---------|---------|
| `tiktoken` | `token_counter.py` |
| `sentence-transformers` | `embedding_search.py` |
| `requests` | `batch_inference.py` |
