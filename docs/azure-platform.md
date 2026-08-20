# Azure Platform Implementation

This project includes a local runnable demo and Azure-ready platform artifacts. The local demo proves the data flow without paid cloud resources; the Azure layer shows how the same design is deployed in a production-style environment.

## Azure Resources

The Bicep template in `infra/main.bicep` provisions:

- Azure Data Lake Storage Gen2 with hierarchical namespace enabled
- ADLS containers for `raw`, `curated`, and `quarantine`
- Azure Data Factory with system-assigned managed identity
- Azure Synapse Analytics workspace
- Azure Key Vault for SaaS API credentials
- Log Analytics workspace
- Diagnostic settings for ADF pipeline, activity, and trigger logs

## Deployment

```powershell
az login
.\scripts\deploy_azure.ps1
```

After deployment, upload Spark jobs:

```powershell
.\scripts\upload_jobs_to_adls.ps1 -StorageAccountName <storage-account-name>
```

## Security Model

- ADF and Synapse use managed identities.
- API secrets are stored in Key Vault.
- ADLS containers separate raw, curated, and quarantine data zones.
- Synapse SQL views expose only reporting-ready fields.
- Diagnostic logs flow into Log Analytics.

## Orchestration

ADF artifacts are stored under `adf/`:

- `linkedServices`: ADLS, Synapse, Key Vault, and generic REST connectors
- `datasets`: REST and ADLS JSON datasets
- `pipelines`: incremental SaaS ingestion pipeline
- `triggers`: hourly trigger sample
- `globalParameters`: environment and storage parameters

## Observability

KQL queries under `monitoring/` support:

- failed pipeline/activity investigation
- daily success-rate tracking
- data freshness checks

## CI/CD

The repo includes:

- GitHub Actions workflow in `.github/workflows/ci.yml`
- Azure DevOps pipeline sample in `azure-devops/pipeline.yml`

Both are included to demonstrate common enterprise deployment options.
