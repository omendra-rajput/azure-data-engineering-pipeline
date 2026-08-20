# Data Contracts

The pipeline uses lightweight source-level contracts to catch schema drift before transformation. Contracts live in `config/schemas.json` and are enforced before records move from raw to curated zones.

## Contract Rules

- Required fields must exist and be non-null.
- Type checks are applied for strings, integers, objects, and timestamp strings.
- Invalid records are routed to quarantine with validation errors.
- Valid records continue to PySpark normalization and Synapse loading.

## Example: Stripe Charges

```json
{
  "required": ["id", "amount", "currency", "created"],
  "types": {
    "id": "string",
    "amount": "integer",
    "currency": "string",
    "created": "integer"
  }
}
```

## Schema Drift Response

| Drift Type | Pipeline Behavior | Owner Action |
| --- | --- | --- |
| New optional field | Continue processing | Add to curated model if useful |
| Missing required field | Quarantine record | Check API release notes or source outage |
| Type change | Quarantine record | Update contract and transformation safely |
| Deleted field | Fail fast | Coordinate downstream model changes |

## Production Extension

In production, contract results should be written to a metadata table with:

- source name
- load date
- batch id
- total records
- valid records
- quarantined records
- schema version
- validation error sample
