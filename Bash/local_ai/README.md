# Bash - Local AI Setup

Shell helpers for preparing and checking local AI environments. Commands below assume you are running from the repository root.

## Scripts

| Script | Purpose |
| --- | --- |
| `check_gpu.sh` | Reports common GPU acceleration signals for Ollama and llama.cpp. |
| `install_llama_cpp.sh` | Clones and builds llama.cpp with CPU, Metal, CUDA, or HIP flags. |
| `setup_python_ai_env.sh` | Creates a Python virtual environment with common local AI packages. |

## Examples

```bash
bash Bash/local_ai/check_gpu.sh
bash Bash/local_ai/install_llama_cpp.sh --accelerator auto --dry-run
bash Bash/local_ai/setup_python_ai_env.sh --venv .venv-local-ai
```

Remove `--dry-run` from `install_llama_cpp.sh` after reviewing the planned clone and build commands.
