<# Pull one or more Ollama models and print installed models. #>

[CmdletBinding()]
param(
    [string[]]$Models = @("llama3", "mistral", "phi3"),
    [string]$HostUrl = "http://localhost:11434"
)

function Test-OllamaServer {
    param([string]$Url)
    try {
        Invoke-RestMethod -Uri "$Url/api/tags" -Method Get -TimeoutSec 5 | Out-Null
        return $true
    } catch {
        return $false
    }
}

if (-not (Get-Command "ollama" -ErrorAction SilentlyContinue)) {
    Write-Error "ollama is not installed or not on PATH."
    exit 1
}

if (-not (Test-OllamaServer -Url $HostUrl)) {
    Write-Error "Ollama server is not reachable at $HostUrl. Start it with: ollama serve"
    exit 1
}

$failed = @()
foreach ($model in $Models) {
    Write-Host "Pulling $model..."
    ollama pull $model
    if ($LASTEXITCODE -ne 0) {
        $failed += $model
    }
}

Write-Host ""
ollama list

if ($failed.Count -gt 0) {
    Write-Error "Failed models: $($failed -join ', ')"
    exit 1
}
