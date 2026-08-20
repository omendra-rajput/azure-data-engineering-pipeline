# Monitoring Queries

Use these KQL queries in the Log Analytics workspace provisioned by `infra/main.bicep`.

## Queries

- `adf_pipeline_failures.kql`: latest failed ADF activities with error payloads
- `pipeline_success_rate.kql`: daily pipeline success rate by pipeline name
- `data_freshness.kql`: last successful raw landing activity by pipeline

## Suggested Alerts

| Alert | Condition | Severity |
| --- | --- | --- |
| Pipeline failure | Failed ADF pipeline run count greater than 0 in 15 minutes | Sev 2 |
| Data freshness breach | No successful priority source load in 60 minutes | Sev 2 |
| Quarantine spike | Quarantined records exceed 5% of batch volume | Sev 3 |
| Latency breach | Average copy activity runtime exceeds 30 minutes | Sev 3 |
