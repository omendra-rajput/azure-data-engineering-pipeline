# Local Demo Walkthrough

Use this walkthrough when presenting the project.

## 1. Start The Demo

```powershell
.\scripts\run_demo.ps1
```

This command runs the full local version of the Azure pipeline:

- starts a mock SaaS API server on port `8000`
- fetches data from 8 REST endpoints
- writes raw JSONL landing files
- validates records against data contracts
- writes curated source datasets
- creates reporting CSV files
- generates `data/reporting/dashboard.html`

## 2. Show The Mock APIs

Open these endpoints while the API server is running:

- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/salesforce/accounts?page=1&page_size=2`
- `http://127.0.0.1:8000/stripe/charges?page=1&page_size=2`
- `http://127.0.0.1:8000/zendesk/tickets?page=1&page_size=2`

## 3. Show The Lake Zones

After the pipeline runs, show these folders:

- `data/raw`: raw API payloads partitioned by source and load date
- `data/curated`: validated datasets with processing metadata
- `data/quarantine`: records that fail schema validation; the mock Zendesk API includes one intentionally malformed ticket
- `data/reporting`: Power BI/Synapse-style reporting outputs

## 4. Show The Reporting Layer

Open:

```text
data/reporting/dashboard.html
```

Then show the generated CSVs:

- `data/reporting/customer_health.csv`
- `data/reporting/pipeline_metrics.csv`

## 5. Connect Back To Azure

Explain that the local mock API and file outputs demonstrate the same pattern as the Azure version:

- Azure Data Factory orchestrates API extraction.
- ADLS Gen2 stores raw, curated, and quarantine zones.
- PySpark transforms source data into customer analytics.
- Synapse SQL exposes governed reporting views.
- Power BI consumes the reporting layer.
