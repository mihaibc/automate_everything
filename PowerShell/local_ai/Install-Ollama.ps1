<# Install Ollama on Windows using winget when available. #>

[CmdletBinding(SupportsShouldProcess = $true)]
param(
    [string]$PackageId = "Ollama.Ollama"
)

function Test-Command {
    param([string]$Name)
    return $null -ne (Get-Command $Name -ErrorAction SilentlyContinue)
}

if (Test-Command "ollama") {
    Write-Host "Ollama is already installed:"
    ollama --version
    exit 0
}

if (-not (Test-Command "winget")) {
    Write-Error "winget is not available. Install Ollama manually from https://ollama.com/download/windows"
    exit 1
}

if ($PSCmdlet.ShouldProcess($PackageId, "Install Ollama")) {
    winget install --id $PackageId --exact
}

if (Test-Command "ollama") {
    Write-Host "Ollama installed successfully."
    ollama --version
} else {
    Write-Warning "Install finished, but ollama was not found on PATH. Open a new terminal and run: ollama --version"
}
