param(
    [string]$ResourceGroupName = "rg-saas-data-pipeline-dev",
    [string]$Location = "eastus",
    [string]$TemplateFile = "infra/main.bicep",
    [string]$ParametersFile = "infra/main.parameters.json"
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command az -ErrorAction SilentlyContinue)) {
    throw "Azure CLI is required. Install Azure CLI, run 'az login', then rerun this script."
}

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location $repoRoot

Write-Host "Creating resource group $ResourceGroupName in $Location..."
az group create --name $ResourceGroupName --location $Location

Write-Host "Deploying Azure resources..."
az deployment group create `
    --resource-group $ResourceGroupName `
    --template-file $TemplateFile `
    --parameters @$ParametersFile

Write-Host "Deployment complete."
