param(
    [string]$EndpointId = $(throw "-EndpointId is required"),
    [string]$ApiKey = $(throw "-ApiKey is required"),
    [string]$Text = "Hello, this is a test of the VoxCPM2 text to speech system.",
    [string]$Voice = "female_en"
)

$ErrorActionPreference = "Stop"

$Body = @{
    input = @{
        text             = $Text
        voice            = $Voice
        response_format  = "base64"
    }
} | ConvertTo-Json

Write-Host "Sending TTS request..." -ForegroundColor Cyan
Write-Host "Endpoint: $EndpointId" -ForegroundColor Gray
Write-Host "Voice: $Voice" -ForegroundColor Gray
Write-Host "Text: $Text" -ForegroundColor Gray
Write-Host ""

try {
    $Response = Invoke-RestMethod `
        -Uri "https://api.runpod.ai/v2/$EndpointId/runsync" `
        -Method Post `
        -Headers @{ Authorization = "Bearer $ApiKey" } `
        -ContentType "application/json" `
        -Body $Body `
        -TimeoutSec 300

    if ($Response.output.error) {
        Write-Host "Error: $($Response.output.error)" -ForegroundColor Red
        exit 1
    }

    $Output = $Response.output
    Write-Host "Generation successful!" -ForegroundColor Green
    Write-Host "Duration: $($Output.duration_secs)s" -ForegroundColor Cyan
    Write-Host "Voice: $($Output.voice)" -ForegroundColor Cyan
    Write-Host "Model: $($Output.model)" -ForegroundColor Cyan

    $OutDir = Join-Path $PSScriptRoot ".." "output"
    New-Item -ItemType Directory -Path $OutDir -Force | Out-Null
    $OutFile = Join-Path $OutDir "test_output.wav"

    $Bytes = [Convert]::FromBase64String($Output.audio)
    [IO.File]::WriteAllBytes($OutFile, $Bytes)

    Write-Host "Audio saved to: $OutFile" -ForegroundColor Green
} catch {
    Write-Host "Request failed: $_" -ForegroundColor Red
    exit 1
}
