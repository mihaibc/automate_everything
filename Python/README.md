# Python Automation Scripts

This directory contains Python automation scripts that currently focus on file management, AI utilities, and local AI workflows.

## Subdirectories

- **[file_management/](file_management/)**: Folder creation and safe file-moving helpers.
- **[ai_utils/](ai_utils/)**: Token counting, prompt building, batch inference, and embedding search.
- **[local_ai/](local_ai/)**: Ollama benchmarking, model reports, Hugging Face downloads, and Modelfile generation.

## How to Use

Install development tooling:

```bash
python3 -m pip install -e ".[dev]"
```

Install optional AI dependencies:

```bash
python3 -m pip install -e ".[ai]"
```

Run a script:

```bash
python Python/file_management/move_files.py --help
python Python/local_ai/ollama_model_report.py --help
```

Run tests:

```bash
python3 -m pytest
```

## Contributing

Contributions are welcome. Please include examples, safe defaults, and tests for reusable behavior. See [CONTRIBUTING.md](../CONTRIBUTING.md).
