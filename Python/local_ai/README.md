# Python - Local AI Utilities

Python helpers for model downloads, Ollama model reporting, benchmarking, and Modelfile generation. Commands below assume you are running from the repository root.

## Scripts

| Script | Purpose |
| --- | --- |
| `benchmark_ollama.py` | Runs repeated prompts against Ollama and reports latency/token metrics. |
| `download_hf_model.py` | Downloads selected files from Hugging Face Hub, with dry-run support. |
| `generate_modelfile.py` | Creates an Ollama `Modelfile` from base model, system prompt, and parameters. |
| `ollama_model_report.py` | Prints installed Ollama models from `/api/tags`. |

## Optional Dependencies

Install optional AI dependencies for the full set of local AI helpers:

```bash
python3 -m pip install -e ".[ai]"
```

Only `download_hf_model.py` requires `huggingface-hub`; it is also listed in [requirements.txt](requirements.txt).

## Examples

```bash
python Python/local_ai/ollama_model_report.py
python Python/local_ai/benchmark_ollama.py --model llama3 --runs 3
python Python/local_ai/download_hf_model.py --repo-id TheBloke/TinyLlama-1.1B-Chat-v1.0-GGUF --include "*.gguf" --dry-run
python Python/local_ai/generate_modelfile.py --from llama3 --system "You are concise." --parameter "temperature 0.2"
```

Use `--dry-run` before downloads when you want to confirm the target repository and file patterns.
