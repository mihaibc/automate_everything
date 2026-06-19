# PowerShell Automation Scripts

PowerShell scripts for Windows-friendly local AI setup and Ollama workflows. Commands below assume you are running from the repository root.

## Subdirectories

- **[local_ai/](local_ai/)**: Install Ollama, pull models, and test a local endpoint.

## How to Use

Test a local Ollama endpoint:

```powershell
PowerShell/local_ai/Test-LocalAIEndpoint.ps1 -Model llama3
```

Install Ollama with a preview first:

```powershell
PowerShell/local_ai/Install-Ollama.ps1 -WhatIf
```

You may need to set the execution policy for your user:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Contributing

Contributions are welcome. New PowerShell scripts should include comment-based help or clear examples, validate external tools, and avoid hard-coded machine-specific paths. See [CONTRIBUTING.md](../CONTRIBUTING.md).
