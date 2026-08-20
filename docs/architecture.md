# Architecture

The pipeline uses Data Factory as the orchestration layer, ADLS Gen2 as the lake, PySpark for distributed transformation, Synapse SQL for consumption models, and Power BI for stakeholder reporting.

## Zones

- Raw: immutable API responses stored by source and load date.
- Curated: conformed Delta/Parquet datasets with duplicate removal and standardized metadata columns.
- Quarantine: rows or files that fail schema validation.

## Reliability Controls

- Metadata-driven source configuration for 8+ SaaS APIs.
- Incremental cursor per source.
- ADF retry policies for transient API and network failures.
- Schema validation before transformation.
- Quarantine handling for incompatible payloads.
- Idempotent partition overwrites for repeatable processing.

## Security

- Managed identities for Azure resource access.
- Secrets stored in Azure Key Vault and referenced by Data Factory.
- ADLS ACLs separated by raw, curated, and reporting zones.
- Synapse views expose only reporting-grade fields.
