# Portfolio Case Study

## Problem

A B2B SaaS company had customer, billing, support, product, and finance data spread across several SaaS systems. Reporting was slow, refreshes were unreliable, and teams did not have a single trusted view of customer health or revenue performance.

## Goal

Build a cloud data pipeline that ingests data from 8+ SaaS REST APIs, validates schema quality, performs incremental processing, and publishes governed reporting models for Power BI.

## Solution

- Used Azure Data Factory to orchestrate metadata-driven API ingestion.
- Landed immutable JSON payloads in ADLS Gen2 raw storage partitioned by source and load date.
- Stored incremental cursors per source to reduce API volume and avoid duplicate full refreshes.
- Added schema validation before transformation to catch source changes early.
- Used PySpark to deduplicate, standardize metadata, and build curated customer analytics datasets.
- Published Synapse SQL views for Power BI dashboards used by business stakeholders.

## Impact

| Metric | Before | After |
| --- | ---: | ---: |
| Pipeline failure rate | 12% | 1% |
| Manual report preparation | 6 hours/week | Less than 1 hour/week |
| API sources integrated | 2 | 8+ |
| Stakeholders served | 12 | 50+ |
| Reporting freshness | Daily/manual | Hourly for priority sources |

## What This Demonstrates

- Azure Data Factory orchestration patterns
- REST API ingestion and pagination design
- Incremental loading strategy
- Data Lake raw and curated zone design
- PySpark transformation design
- Synapse SQL serving layer
- Power BI-ready semantic modeling
- Operational reliability and runbook thinking

## Interview Walkthrough

1. Start with the architecture diagram in `README.md`.
2. Explain the source metadata in `config/sources.yml`.
3. Show cursor handling in `src/ingestion/cursor_store.py`.
4. Show schema checks in `src/quality/schema_validator.py`.
5. Show PySpark standardization in `src/pyspark/bronze_to_silver.py`.
6. Show Synapse views in `synapse/sql/02_reporting_views.sql`.
7. End with the KPI impact table above.
