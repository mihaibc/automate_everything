# Python AI Utilities

Command-line utilities for token counting, prompt assembly, batch inference, and semantic search. Commands below assume you are running from the repository root.

## Setup

```bash
python3 -m pip install -e ".[ai]"
```

## Scripts

### `token_counter.py`

Count tokens before sending text to an LLM.

```bash
# Inline text
python Python/ai_utils/token_counter.py --text "Hello, world!" --model gpt-4

# Pipe from stdin
cat document.txt | python Python/ai_utils/token_counter.py --model cl100k_base

# Verbose output
python Python/ai_utils/token_counter.py --text "Some long document..." --model gpt-4o --verbose
```

Supported models/encodings: `gpt-4`, `gpt-4o`, `gpt-3.5-turbo`, `cl100k_base`, `o200k_base`, `p50k_base`.

### `prompt_builder.py`

Build structured prompt payloads from inline text or templates.

```bash
# Inline with variable substitution
python Python/ai_utils/prompt_builder.py --user "Summarize {topic} in 3 bullets" --vars topic=Docker

# From files, output piped to Ollama
python Python/ai_utils/prompt_builder.py \
  --system examples/templates/system.txt \
  --user examples/templates/user.txt \
  --vars topic=Ollama | \
  curl -s http://localhost:11434/api/chat -d @-

# Target a specific model
python Python/ai_utils/prompt_builder.py --user "Hello!" --model mistral
```

Template files use `{placeholder}` syntax. Missing variables produce a warning but don't fail.

### `batch_inference.py`

Run many prompts in parallel against an OpenAI-compatible endpoint. Input is a `.jsonl` file where each line contains a JSON object with `messages` or `prompt`.

```bash
# Against a local Ollama instance
python Python/ai_utils/batch_inference.py \
  --input examples/prompts/prompts.jsonl \
  --output results.jsonl

# Against OpenAI
python Python/ai_utils/batch_inference.py \
  --input prompts.jsonl \
  --endpoint https://api.openai.com/v1 \
  --model gpt-4o \
  --api-key $OPENAI_API_KEY \
  --workers 8

# Example input line (prompts.jsonl):
# {"messages": [{"role": "user", "content": "What is Kubernetes?"}]}
```

Results are written as JSONL with `status`, `output`, and `elapsed_s` fields per entry.

### `embedding_search.py`

Build a local embedding index over `.txt` files and search it with natural language.

```bash
# Step 1: Build an index from a directory of .txt files
python Python/ai_utils/embedding_search.py index --dir ./my_docs

# Step 2: Search
python Python/ai_utils/embedding_search.py search --query "how to handle authentication"

# Top 10 results as JSON
python Python/ai_utils/embedding_search.py search --query "deployment pipeline" --top 10 --json
```

The index is saved as `embedding_index.json`. The default model is `all-MiniLM-L6-v2`, which runs locally after the initial model download.

## Dependencies

| Package | Used by |
| --- | --- |
| `tiktoken` | `token_counter.py` |
| `sentence-transformers` | `embedding_search.py` |
| `requests` | `batch_inference.py` |
