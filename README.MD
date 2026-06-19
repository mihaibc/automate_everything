# Automate Everything

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Issues](https://img.shields.io/github/issues/mihaibc/automate_everything)](https://github.com/mihaibc/automate_everything/issues)
[![Stars](https://img.shields.io/github/stars/mihaibc/automate_everything?style=flat)](https://github.com/mihaibc/automate_everything/stargazers)

Practical automation scripts for developer workflows and local AI setup.

The repository focuses on scripts that are easy to inspect, safe to run, documented with examples, and covered by lightweight checks. The strongest current areas are local LLM setup, Ollama workflows, AI utilities, and file management helpers.

---

## Table of Contents

- [What's Inside](#whats-inside)
- [Quick Start](#quick-start)
- [Quality Gates](#quality-gates)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## What's inside

| Area | Scripts | Docs |
| --- | --- | --- |
| Python file management | `create_folder_structure.py`, `move_files.py` | [Python/README.md](Python/README.md) |
| Python AI utilities | `token_counter.py`, `prompt_builder.py`, `batch_inference.py`, `embedding_search.py` | [Python/ai_utils/README.md](Python/ai_utils/README.md) |
| Python local AI | `benchmark_ollama.py`, `download_hf_model.py`, `generate_modelfile.py`, `ollama_model_report.py` | [Python/local_ai/README.md](Python/local_ai/README.md) |
| Bash Ollama setup | `install_ollama.sh`, `pull_models.sh`, `run_inference.sh` | [Bash/README.md](Bash/README.md) |
| Bash local AI | `check_gpu.sh`, `install_llama_cpp.sh`, `setup_python_ai_env.sh` | [Bash/local_ai/README.md](Bash/local_ai/README.md) |
| PowerShell local AI | `Install-Ollama.ps1`, `Pull-OllamaModels.ps1`, `Test-LocalAIEndpoint.ps1` | [PowerShell/local_ai/README.md](PowerShell/local_ai/README.md) |

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

**Count tokens before sending text to an LLM**

```bash
python3 -m pip install -e ".[ai]"
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
python Python/ai_utils/batch_inference.py --input prompts.jsonl --output results.jsonl
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

- [ ] More local model runners: llama.cpp server, LM Studio, vLLM, and Open WebUI helpers.
- [ ] Cross-platform smoke tests for PowerShell scripts.
- [ ] More file-management helpers with dry-run and rollback support.
- [ ] Script metadata index for discoverability.
- [ ] First Go, C++, and Perl scripts after a concrete use case is ready.

Have a script that fits? [Open a feature request](https://github.com/mihaibc/automate_everything/issues/new?template=feature_request.md) or submit a PR.

---

## Contributing

Contributions are welcome: new scripts, bug fixes, tests, examples, and documentation improvements. Please read [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md), and the [Code of Conduct](CODE_OF_CONDUCT.md) before opening a PR.

---

## License

MIT — see [LICENSE](LICENSE) for details.
