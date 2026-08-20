# Azure Deployment Checklist

## Azure Resources

- Resource group created through `scripts/deploy_azure.ps1`.
- ADLS Gen2 account created with hierarchical namespace enabled by `infra/main.bicep`.
- Containers created: `raw`, `curated`, `quarantine`.
- Azure Data Factory created with system-assigned managed identity.
- Azure Synapse workspace created.
- Key Vault created for API credentials.
- Log Analytics workspace created.
- ADF diagnostic settings enabled.
- Managed identities assigned RBAC access to ADLS and Key Vault.

## Data Factory

- Import linked services from `adf/linkedServices`.
- Import datasets from `adf/datasets`.
- Import pipeline from `adf/pipelines`.
- Import trigger from `adf/triggers`.
- Configure global parameters from `adf/globalParameters`.
- Replace placeholder endpoint, storage, and Synapse values.
- Configure Key Vault-backed secrets for SaaS API tokens.
- Add tumbling-window or scheduled triggers.

## Synapse

- Upload PySpark jobs from `src/pyspark`.
- Run `synapse/sql/01_create_external_objects.sql`.
- Run `synapse/sql/02_reporting_views.sql`.
- Validate external table access to curated ADLS paths.

## Power BI

- Connect to Synapse SQL endpoint.
- Import reporting views.
- Add measures from `powerbi/README.md`.
- Configure scheduled refresh.
- Share dashboard with target workspace group.

## Go-Live Validation

- Run one backfill batch.
- Run one incremental batch.
- Confirm schema validation logs.
- Confirm quarantine folder behavior.
- Confirm Power BI refresh completes.
- Confirm stakeholder KPIs match expected source totals.
- Confirm Log Analytics receives ADF pipeline and activity logs.
