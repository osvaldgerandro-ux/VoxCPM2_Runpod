param(
    [string]$Config = "deploy/voxcpm2_dev.yaml"
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Split-Path -Parent $PSScriptRoot

Write-Host "Deploying VoxCPM2 TTS endpoint using config: $Config" -ForegroundColor Cyan
Write-Host "Project root: $ProjectRoot" -ForegroundColor Cyan

Set-Location -Path $ProjectRoot
flash deploy --config $Config

if ($LASTEXITCODE -eq 0) {
    Write-Host "Deployment successful!" -ForegroundColor Green
} else {
    Write-Host "Deployment failed with exit code $LASTEXITCODE" -ForegroundColor Red
    exit $LASTEXITCODE
}
