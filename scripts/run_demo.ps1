$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Starting mock SaaS API server..."
$dataPath = Join-Path $repoRoot "data"
if (Test-Path $dataPath) {
    Write-Host "Resetting local demo output folder..."
    Remove-Item -Path $dataPath -Recurse -Force
}

$server = Start-Process -FilePath python -ArgumentList "-m", "src.demo.mock_saas_api", "--port", "8000" -PassThru -WindowStyle Hidden

try {
    Start-Sleep -Seconds 2
    Write-Host "Checking API health..."
    Invoke-RestMethod -Uri "http://127.0.0.1:8000/health" | ConvertTo-Json

    Write-Host "Running local ETL pipeline..."
    python -m src.demo.run_local_pipeline

    $dashboard = Join-Path $repoRoot "data\reporting\dashboard.html"
    Write-Host "Opening dashboard: $dashboard"
    Start-Process $dashboard
}
finally {
    if ($server -and -not $server.HasExited) {
        Stop-Process -Id $server.Id
        Write-Host "Stopped mock SaaS API server."
    }
}
