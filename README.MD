# Automate Everything

[![Checks](https://github.com/mihaibc/automate_everything/actions/workflows/lint.yml/badge.svg)](https://github.com/mihaibc/automate_everything/actions/workflows/lint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Issues](https://img.shields.io/github/issues/mihaibc/automate_everything)](https://github.com/mihaibc/automate_everything/issues)
[![Stars](https://img.shields.io/github/stars/mihaibc/automate_everything?style=flat)](https://github.com/mihaibc/automate_everything/stargazers)

Practical automation scripts for developers who want local AI workflows, safer file operations, and repeatable command-line utilities they can inspect before running.

This repo is intentionally script-first: small tools, clear commands, safe defaults, and lightweight tests. The strongest current areas are Ollama setup, local model tooling, prompt utilities, semantic search, and file management helpers.

---

## Table of Contents

- [Why Use This](#why-use-this)
- [What's Inside](#whats-inside)
- [Quick Start](#quick-start)
- [Local AI Recipes](#local-ai-recipes)
- [Quality Gates](#quality-gates)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Why Use This

- **Readable by default**: every script is meant to be opened, understood, and adapted.
- **Safer automation**: file-moving and setup helpers prefer explicit inputs, dry runs, and clear failures.
- **Local AI friendly**: Ollama, llama.cpp, Hugging Face model downloads, Modelfiles, endpoint checks, and benchmarking are covered.
- **Contributor ready**: tests, linting, shell checks, issue templates, PR checklist, security notes, and examples are already in place.

---

## What's Inside

| Area | Scripts | Docs |
| --- | --- | --- |
| Python file management | `create_folder_structure.py`, `move_files.py` | [Python/README.md](Python/README.md) |
| Python AI utilities | `token_counter.py`, `prompt_builder.py`, `batch_inference.py`, `embedding_search.py` | [Python/ai_utils/README.md](Python/ai_utils/README.md) |
| Python local AI | `benchmark_ollama.py`, `download_hf_model.py`, `generate_modelfile.py`, `ollama_model_report.py` | [Python/local_ai/README.md](Python/local_ai/README.md) |
| Bash Ollama setup | `install_ollama.sh`, `pull_models.sh`, `run_inference.sh` | [Bash/README.md](Bash/README.md) |
| Bash local AI | `check_gpu.sh`, `install_llama_cpp.sh`, `setup_python_ai_env.sh` | [Bash/local_ai/README.md](Bash/local_ai/README.md) |
| PowerShell local AI | `Install-Ollama.ps1`, `Pull-OllamaModels.ps1`, `Test-LocalAIEndpoint.ps1` | [PowerShell/local_ai/README.md](PowerShell/local_ai/README.md) |
| Perl developer utilities | `jsonl_validate.pl`, `todo_report.pl`, `env_audit.pl`, `replace_in_files.pl`, `log_summary.pl`, `repo_lint.pl` | [Perl/README.md](Perl/README.md) |

---

## Quick Start

**Clone the repo**

```bash
git clone https://github.com/mihaibc/automate_everything.git
cd automate_everything
```

**Install development tools**

```bash
python3 -m pip install -e ".[dev]"
```

**Install optional AI dependencies**

```bash
python3 -m pip install -e ".[ai]"
```

**Count tokens before sending text to an LLM**

```bash
echo "Your text here" | python Python/ai_utils/token_counter.py --model gpt-4
```

**Set up a local LLM with Ollama**

```bash
bash Bash/llm_setup/install_ollama.sh
bash Bash/llm_setup/pull_models.sh
bash Bash/llm_setup/run_inference.sh --prompt "Explain Kubernetes in one sentence"
```

**Check local AI hardware signals**

```bash
bash Bash/local_ai/check_gpu.sh
```

**Organize files by extension safely**

```bash
python Python/file_management/move_files.py \
  --source ~/Downloads \
  --destination ~/Documents/PDFs \
  --extensions pdf \
  --dry-run
```

**Run batch LLM inference from a JSONL file**

```bash
python Python/ai_utils/batch_inference.py \
  --input examples/prompts/prompts.jsonl \
  --output results.jsonl
```

---

## Local AI Recipes

**Inspect local acceleration options**

```bash
bash Bash/local_ai/check_gpu.sh
```

**Build llama.cpp**

```bash
bash Bash/local_ai/install_llama_cpp.sh --accelerator auto --dry-run
```

Remove `--dry-run` when the planned clone and build path looks right.

**Create a Python local-AI environment**

```bash
bash Bash/local_ai/setup_python_ai_env.sh --venv .venv-local-ai
```

**List installed Ollama models**

```bash
python Python/local_ai/ollama_model_report.py
```

**Benchmark an Ollama model**

```bash
python Python/local_ai/benchmark_ollama.py --model llama3 --runs 3
```

**Generate an Ollama Modelfile**

```bash
python Python/local_ai/generate_modelfile.py \
  --from llama3 \
  --system "You are concise and practical." \
  --parameter "temperature 0.2"
```

**Windows Ollama smoke test**

```powershell
PowerShell/local_ai/Test-LocalAIEndpoint.ps1 -Model llama3
```

---

## Quality Gates

Run the same checks locally that CI runs:

```bash
make check
```

Individual commands:

```bash
make lint
make test
make shellcheck
make py-compile
make perl-syntax
make perl-test
make docs-check
```

Install `shellcheck` separately if your platform does not include it.

---

## Repository Standards

New scripts should include:

- A clear CLI with `--help`.
- Safe defaults and `--dry-run` for destructive operations.
- Quoted shell variables and strict Bash mode where relevant.
- No secrets, tokens, or personal paths.
- README usage examples.
- Tests for Python behavior when practical.

---

## Roadmap

- [ ] More local model runners: llama.cpp server mode, LM Studio, vLLM, and Open WebUI helpers.
- [ ] Cross-platform smoke tests for PowerShell scripts.
- [ ] More file-management helpers with dry-run and rollback support.
- [ ] Script metadata index for discoverability.
- [ ] First Go and C++ scripts after a concrete use case is ready.

Have a script that fits? [Open a feature request](https://github.com/mihaibc/automate_everything/issues/new?template=feature_request.md) or submit a PR.

---

## Contributing

Contributions are welcome: new scripts, bug fixes, tests, examples, and documentation improvements. Please read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and the [Code of Conduct](CODE_OF_CONDUCT.md) before opening a PR.

---

## License

MIT. See [LICENSE](LICENSE) for details.
