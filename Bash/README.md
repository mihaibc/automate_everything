
# Bash Automation Scripts

This directory contains Bash scripts for local AI setup and command-line automation.

## Subdirectories

- **[llm_setup/](llm_setup/)**: Install Ollama, pull models, and run local LLM inference from the command line.
- **[local_ai/](local_ai/)**: GPU checks, llama.cpp builds, and local Python AI environments.

## How to Use

Run scripts with `bash`:

```bash
bash Bash/llm_setup/run_inference.sh --help
bash Bash/local_ai/check_gpu.sh
```

Run shell checks:

```bash
shellcheck Bash/**/*.sh
```

## Contributing

Contributions are welcome. New Bash scripts should use `set -euo pipefail`, quote variables, validate dependencies, and include a `--help` path. See [CONTRIBUTING.md](../CONTRIBUTING.md).
