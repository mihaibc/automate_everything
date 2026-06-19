# PowerShell Automation Scripts

This directory contains PowerShell scripts for Windows-friendly local AI setup and Ollama workflows.

## Subdirectories

- **[local_ai/](local_ai/)**: Install Ollama, pull models, and test a local endpoint.

## How to Use

Run a script:

```powershell
PowerShell/local_ai/Test-LocalAIEndpoint.ps1 -Model llama3
```

You may need to set the execution policy for your user:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Contributing

Contributions are welcome. New PowerShell scripts should include comment-based help or clear examples, validate external tools, and avoid hard-coded machine-specific paths. See [CONTRIBUTING.md](../CONTRIBUTING.md).
