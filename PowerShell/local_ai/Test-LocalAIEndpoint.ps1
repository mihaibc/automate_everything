<# Test an Ollama-compatible local chat endpoint. #>

[CmdletBinding()]
param(
    [string]$HostUrl = "http://localhost:11434",
    [string]$Model = "llama3",
    [string]$Prompt = "Reply with one short sentence confirming the local model works.",
    [switch]$Json
)

$body = @{
    model = $Model
    stream = $false
    messages = @(
        @{
            role = "user"
            content = $Prompt
        }
    )
} | ConvertTo-Json -Depth 5

try {
    $response = Invoke-RestMethod -Uri "$HostUrl/api/chat" -Method Post -Body $body -ContentType "application/json" -TimeoutSec 120
} catch {
    Write-Error "Request failed: $($_.Exception.Message)"
    exit 1
}

if ($Json) {
    $response | ConvertTo-Json -Depth 10
} else {
    $response.message.content
}
