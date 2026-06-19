# Python - Local AI Utilities

Python helpers for managing local AI models and Ollama workflows.

## Scripts

| Script | Purpose |
| --- | --- |
| `benchmark_ollama.py` | Runs repeated prompts against Ollama and reports latency/token metrics. |
| `download_hf_model.py` | Downloads selected files from Hugging Face Hub, with dry-run support. |
| `generate_modelfile.py` | Creates an Ollama `Modelfile` from base model, system prompt, and parameters. |
| `ollama_model_report.py` | Prints installed Ollama models from `/api/tags`. |

## Optional Dependencies

Only `download_hf_model.py` requires an extra dependency:

```bash
pip install -r Python/local_ai/requirements.txt
```

## Examples

```bash
python Python/local_ai/ollama_model_report.py
python Python/local_ai/benchmark_ollama.py --model llama3 --runs 3
python Python/local_ai/download_hf_model.py --repo-id some/model --include "*.gguf" --dry-run
python Python/local_ai/generate_modelfile.py --from llama3 --system "You are concise." --parameter "temperature 0.2"
```
