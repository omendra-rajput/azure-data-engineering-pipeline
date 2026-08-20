param(
    [Parameter(Mandatory = $true)]
    [string]$StorageAccountName,

    [string]$Container = "curated"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw "Azure CLI is required. Install Azure CLI and run 'az login'."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

az storage fs directory create `
    --account-name $StorageAccountName `
    --file-system $Container `
    --name jobs `
    --auth-mode login

az storage fs file upload `
    --account-name $StorageAccountName `
    --file-system $Container `
    --path jobs/bronze_to_silver.py `
    --source src/pyspark/bronze_to_silver.py `
    --overwrite true `
    --auth-mode login

az storage fs file upload `
    --account-name $StorageAccountName `
    --file-system $Container `
    --path jobs/build_customer_360.py `
    --source src/pyspark/build_customer_360.py `
    --overwrite true `
    --auth-mode login

Write-Host "Uploaded PySpark jobs to abfss://$Container@$StorageAccountName.dfs.core.windows.net/jobs/"
