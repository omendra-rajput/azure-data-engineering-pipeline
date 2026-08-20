# Azure Infrastructure

This folder contains Bicep infrastructure for the Azure SaaS data engineering pipeline.

## Resources

- ADLS Gen2 storage account
- `raw`, `curated`, and `quarantine` containers
- Azure Data Factory
- Azure Synapse workspace
- Azure Key Vault
- Log Analytics workspace
- ADF diagnostic settings

## Deploy

```powershell
az login
.\scripts\deploy_azure.ps1
```

## Notes

The Synapse SQL admin password in `main.bicep` is a placeholder to keep the portfolio template readable. For real deployments, pass it as a secure parameter from Key Vault or a CI/CD secret store.
