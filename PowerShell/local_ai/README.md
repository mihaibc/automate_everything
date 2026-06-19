# PowerShell - Local AI Setup

Windows-friendly helpers for Ollama-based local AI workflows.

## Scripts

| Script | Purpose |
| --- | --- |
| `Install-Ollama.ps1` | Installs Ollama with `winget` when available. |
| `Pull-OllamaModels.ps1` | Pulls one or more local models and prints `ollama list`. |
| `Test-LocalAIEndpoint.ps1` | Sends a test chat request to a local Ollama endpoint. |

## Examples

```powershell
PowerShell/local_ai/Install-Ollama.ps1 -WhatIf
PowerShell/local_ai/Pull-OllamaModels.ps1 -Models llama3,mistral
PowerShell/local_ai/Test-LocalAIEndpoint.ps1 -Model llama3
```
