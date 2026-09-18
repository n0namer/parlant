param(
    [string]$BaseUrl = "http://127.0.0.1:19280/v1",
    [string]$Model = "openai/fcm:fast-coding",
    [string]$ApiKey = "local-fcm",
    [string]$Home = "",
    [int]$Port = 8800,
    [string]$Venv = ".venv-mnnz-fcm"
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..\..")).Path
Set-Location $repo

if ([string]::IsNullOrWhiteSpace($Home)) {
    $stamp = Get-Date -Format "yyyyMMdd-HHmmss-fff"
    $Home = Join-Path $repo ".parlant-data\fcm-$stamp"
}

$server = Join-Path $repo "$Venv\Scripts\parlant-server.exe"
if (-not (Test-Path $server)) {
    throw "Missing $server. Run mnnz/fcm/bootstrap.ps1 first."
}

$env:PARLANT_HOME = $Home
$env:LITELLM_PROVIDER_MODEL_NAME = $Model
$env:LITELLM_PROVIDER_BASE_URL = $BaseUrl
$env:LITELLM_PROVIDER_API_KEY = $ApiKey

Write-Host "PARLANT_HOME=$Home"
Write-Host "LITELLM_PROVIDER_MODEL_NAME=$Model"
Write-Host "LITELLM_PROVIDER_BASE_URL=$BaseUrl"
Write-Host "PORT=$Port"

& $server run --litellm --host 127.0.0.1 --port $Port --log-level info
