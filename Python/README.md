# Python Automation Scripts

Python scripts for file management, prompt workflows, semantic search, and local AI tooling. Commands below assume you are running from the repository root.

## Subdirectories

- **[file_management/](file_management/)**: Folder creation and safe file-moving helpers.
- **[ai_utils/](ai_utils/)**: Token counting, prompt building, batch inference, and embedding search.
- **[local_ai/](local_ai/)**: Ollama benchmarking, model reports, Hugging Face downloads, and Modelfile generation.

## How to Use

Install development tooling when you plan to run tests or contribute:

```bash
python3 -m pip install -e ".[dev]"
```

Install optional AI dependencies when you want token counting, embedding search, batch inference, or Hugging Face downloads:

```bash
python3 -m pip install -e ".[ai]"
```

Inspect a script before using it:

```bash
python Python/file_management/move_files.py --help
python Python/local_ai/ollama_model_report.py --help
```

Try a safe file move preview:

```bash
python Python/file_management/move_files.py \
  --source ~/Downloads \
  --destination ~/Documents/PDFs \
  --extensions pdf \
  --dry-run
```

Run tests:

```bash
python3 -m pytest
```

## Contributing

Contributions are welcome. Please include examples, safe defaults, and tests for reusable behavior. See [CONTRIBUTING.md](../CONTRIBUTING.md).
