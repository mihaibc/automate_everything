# Automate Everything

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
[![Issues](https://img.shields.io/github/issues/mihaibc/automate_everything)](https://github.com/mihaibc/automate_everything/issues)
[![Stars](https://img.shields.io/github/stars/mihaibc/automate_everything?style=flat)](https://github.com/mihaibc/automate_everything/stargazers)

> A multi-language collection of automation scripts — from file management to local LLM inference setup. Pick a language, grab a script, automate something.

---

## Table of Contents

- [What's inside](#whats-inside)
- [Quick Start](#quick-start)
- [Languages](#languages)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [Contributors](#contributors)
- [License](#license)

---

## What's inside

| Language | Category | Scripts | Docs |
|----------|----------|---------|------|
| Python | File Management | `create_folder_structure.py`, `move_files.py` | [Python/README.md](Python/README.md) |
| Python | AI Utils | `token_counter.py`, `prompt_builder.py`, `batch_inference.py`, `embedding_search.py` | [Python/ai_utils/README.md](Python/ai_utils/README.md) |
| Bash | LLM Setup | `install_ollama.sh`, `pull_models.sh`, `run_inference.sh` | [Bash/README.md](Bash/README.md) |
| Go | Cloud / CI-CD | *(coming soon)* | [Go/README.md](Go/README.md) |
| C++ | Performance / Low-level | *(coming soon)* | [C++/README.md](C++/README.md) |
| Perl | Text Processing | *(coming soon)* | [Perl/README.md](Perl/README.md) |
| PowerShell | Windows Automation | *(coming soon)* | [PowerShell/README.md](PowerShell/README.md) |

---

## Quick Start

**Clone the repo**

```bash
git clone https://github.com/mihaibc/automate_everything.git
cd automate_everything
```

**Count tokens before sending text to an LLM**

```bash
pip install tiktoken
echo "Your text here" | python Python/ai_utils/token_counter.py --model gpt-4
```

**Set up a local LLM with Ollama**

```bash
bash Bash/llm_setup/install_ollama.sh
bash Bash/llm_setup/pull_models.sh
bash Bash/llm_setup/run_inference.sh --prompt "Explain Kubernetes in one sentence"
```

**Organise files by extension**

```bash
python Python/file_management/move_files.py
# prompts for source path, destination path, and extensions (e.g. pdf,jpg)
```

**Run batch LLM inference from a JSONL file**

```bash
pip install requests
python Python/ai_utils/batch_inference.py --input prompts.jsonl --output results.jsonl
```

---

## Languages

### [Python](Python/README.md)
General-purpose automation, file management, AI/LLM utilities, web scraping, and data processing. Rich ecosystem, easy to read, widely supported.

### [Bash](Bash/README.md)
Unix/Linux system administration, local LLM environment setup, file management, and task scheduling. Excellent for quick glue scripts and shell pipelines.

### [Go](Go/README.md)
Cloud automation, CI/CD pipelines, and network tooling. High performance, built-in concurrency, ideal for cloud-native tasks.

### [C++](C++/README.md)
Performance-critical automation and low-level system tasks. Direct hardware access and maximum throughput where it counts.

### [Perl](Perl/README.md)
Text processing, log parsing, and legacy system administration. Unmatched for regex-heavy tasks and CPAN ecosystem integration.

### [PowerShell](PowerShell/README.md)
Windows system administration, Active Directory management, and automating Windows-based applications. Deep .NET integration.

---

## Roadmap

- [ ] Python — web scraping utilities (`requests`, `BeautifulSoup`)
- [ ] Python — data processing helpers (`pandas`, `csv`, `json`)
- [ ] Bash — system administration scripts (disk monitoring, log rotation)
- [ ] Go — cloud automation (AWS/GCP/Azure CLI wrappers)
- [ ] Go — CI/CD helpers (build matrix, changelog generator)
- [ ] PowerShell — Active Directory automation scripts
- [ ] Perl — log parsing and report generation

Have a script that fits? [Open a feature request](https://github.com/mihaibc/automate_everything/issues/new?template=feature_request.md) or submit a PR.

---

## Contributing

Contributions are welcome — new scripts, bug fixes, documentation improvements. Please read [CONTRIBUTING.md](CONTRIBUTING.md) and follow the [Code of Conduct](CODE_OF_CONDUCT.md) before opening a PR.

---

## Contributors

[![Contributors](https://contrib.rocks/image?repo=mihaibc/automate_everything)](https://github.com/mihaibc/automate_everything/graphs/contributors)

---

## License

MIT — see [LICENSE](LICENSE) for details.
