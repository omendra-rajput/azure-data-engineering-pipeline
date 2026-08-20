from __future__ import annotations

import argparse
import csv
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

from src.ingestion.cursor_store import CursorStore
from src.quality.schema_validator import validate_record


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fetch_all(base_url: str, source: dict[str, str], cursor_value: str) -> list[dict]:
    page = 1
    rows: list[dict] = []
    while True:
        query = urlencode({"page": page, "page_size": 2, "since": cursor_value})
        with urlopen(f"{base_url}{source['path']}?{query}", timeout=15) as response:
            payload = json.loads(response.read().decode("utf-8"))
        rows.extend(payload["data"])
        if not payload.get("next"):
            return rows
        page += 1


def write_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")


def read_jsonl(path: Path) -> list[dict]:
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def validate_and_curate(source_name: str, rows: list[dict], schema: dict, data_root: Path) -> tuple[int, int]:
    valid_rows: list[dict] = []
    invalid_rows: list[dict] = []

    for row in rows:
        result = validate_record(row, schema)
        enriched = dict(row)
        enriched["_source_name"] = source_name
        enriched["_processed_at"] = datetime.now(timezone.utc).isoformat()
        if result.valid:
            valid_rows.append(enriched)
        else:
            enriched["_validation_errors"] = result.errors
            invalid_rows.append(enriched)

    write_jsonl(data_root / "curated" / source_name / f"{source_name}.jsonl", valid_rows)
    if invalid_rows:
        write_jsonl(data_root / "quarantine" / source_name / "invalid_records.jsonl", invalid_rows)

    return len(valid_rows), len(invalid_rows)


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def build_customer_health(data_root: Path) -> list[dict]:
    accounts = read_jsonl(data_root / "curated" / "salesforce_accounts" / "salesforce_accounts.jsonl")
    charges = read_jsonl(data_root / "curated" / "stripe_charges" / "stripe_charges.jsonl")
    tickets = read_jsonl(data_root / "curated" / "zendesk_tickets" / "zendesk_tickets.jsonl")
    events = read_jsonl(data_root / "curated" / "google_analytics_events" / "google_analytics_events.jsonl")
    invoices = read_jsonl(data_root / "curated" / "netsuite_invoices" / "netsuite_invoices.jsonl")

    revenue_by_customer: defaultdict[str, int] = defaultdict(int)
    for charge in charges:
        revenue_by_customer[str(charge["customer_id"])] += int(charge["amount"])

    tickets_by_customer = Counter(str(ticket["customer_id"]) for ticket in tickets)
    events_by_customer = Counter(str(event["customer_id"]) for event in events)
    open_invoice_by_customer: defaultdict[str, int] = defaultdict(int)
    for invoice in invoices:
        open_invoice_by_customer[str(invoice["customer_id"])] += int(invoice["amountDue"])

    output: list[dict] = []
    for account in accounts:
        customer_id = str(account["Id"])
        ticket_count = tickets_by_customer[customer_id]
        open_invoice_amount = open_invoice_by_customer[customer_id]
        if ticket_count >= 2 or open_invoice_amount > 10000:
            health_status = "High Risk"
        elif ticket_count == 1:
            health_status = "Watch"
        else:
            health_status = "Healthy"

        output.append(
            {
                "customer_id": customer_id,
                "customer_name": account["Name"],
                "region": account.get("Region", "Unknown"),
                "lifetime_revenue": revenue_by_customer[customer_id],
                "ticket_count": ticket_count,
                "product_events": events_by_customer[customer_id],
                "open_invoice_amount": open_invoice_amount,
                "health_status": health_status,
            }
        )

    write_csv(
        data_root / "reporting" / "customer_health.csv",
        output,
        [
            "customer_id",
            "customer_name",
            "region",
            "lifetime_revenue",
            "ticket_count",
            "product_events",
            "open_invoice_amount",
            "health_status",
        ],
    )
    return output


def build_dashboard(data_root: Path, customer_health: list[dict], metrics: list[dict]) -> Path:
    total_revenue = sum(int(row["lifetime_revenue"]) for row in customer_health)
    high_risk = sum(1 for row in customer_health if row["health_status"] == "High Risk")
    success_rate = 1 - (sum(row["invalid_records"] for row in metrics) / max(sum(row["records"] for row in metrics), 1))
    rows_html = "\n".join(
        f"<tr><td>{row['customer_id']}</td><td>{row['customer_name']}</td><td>{row['region']}</td><td>${int(row['lifetime_revenue']):,}</td><td>{row['ticket_count']}</td><td>{row['health_status']}</td></tr>"
        for row in customer_health
    )
    source_rows = "\n".join(
        f"<tr><td>{row['source']}</td><td>{row['records']}</td><td>{row['valid_records']}</td><td>{row['invalid_records']}</td></tr>"
        for row in metrics
    )
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Azure SaaS Pipeline Demo</title>
  <style>
    body {{ margin: 0; font-family: Arial, sans-serif; color: #172033; background: #f4f7fb; }}
    header {{ background: #10243e; color: white; padding: 28px 36px; }}
    main {{ padding: 28px 36px; }}
    .grid {{ display: grid; grid-template-columns: repeat(4, minmax(160px, 1fr)); gap: 16px; margin-bottom: 28px; }}
    .card {{ background: white; border: 1px solid #d9e2ef; border-radius: 8px; padding: 18px; }}
    .label {{ color: #5c6f88; font-size: 13px; }}
    .value {{ font-size: 28px; font-weight: 700; margin-top: 8px; }}
    table {{ width: 100%; border-collapse: collapse; background: white; border: 1px solid #d9e2ef; margin-bottom: 28px; }}
    th, td {{ padding: 10px 12px; border-bottom: 1px solid #e7edf5; text-align: left; }}
    th {{ background: #eaf0f7; font-size: 13px; color: #31445c; }}
  </style>
</head>
<body>
  <header>
    <h1>Azure SaaS Data Engineering Pipeline</h1>
    <p>Local demo output generated from 8 mock SaaS REST APIs through raw, curated, quarantine, and reporting zones.</p>
  </header>
  <main>
    <section class="grid">
      <div class="card"><div class="label">API Sources</div><div class="value">{len(metrics)}</div></div>
      <div class="card"><div class="label">Pipeline Success Rate</div><div class="value">{success_rate:.1%}</div></div>
      <div class="card"><div class="label">Total Revenue</div><div class="value">${total_revenue:,}</div></div>
      <div class="card"><div class="label">High-Risk Customers</div><div class="value">{high_risk}</div></div>
    </section>
    <h2>Customer Health Reporting View</h2>
    <table><thead><tr><th>Customer ID</th><th>Name</th><th>Region</th><th>Revenue</th><th>Tickets</th><th>Status</th></tr></thead><tbody>{rows_html}</tbody></table>
    <h2>Pipeline Run Metrics</h2>
    <table><thead><tr><th>Source</th><th>Raw Records</th><th>Valid</th><th>Quarantined</th></tr></thead><tbody>{source_rows}</tbody></table>
  </main>
</body>
</html>"""
    output = data_root / "reporting" / "dashboard.html"
    output.write_text(html, encoding="utf-8")
    return output


def run_pipeline(config_path: Path, schema_path: Path, data_root: Path) -> Path:
    config = read_json(config_path)
    schemas = read_json(schema_path)
    cursor_store = CursorStore(data_root / "state" / "cursors.json")
    load_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    metrics: list[dict] = []

    for source in config["sources"]:
        source_name = source["name"]
        cursor_value = cursor_store.load(source_name)
        rows = fetch_all(config["base_url"], source, cursor_value)
        raw_path = data_root / "raw" / source_name / f"load_date={load_date}" / "part-00000.jsonl"
        write_jsonl(raw_path, rows)
        valid_count, invalid_count = validate_and_curate(source_name, rows, schemas[source_name], data_root)
        metrics.append(
            {
                "source": source_name,
                "records": len(rows),
                "valid_records": valid_count,
                "invalid_records": invalid_count,
            }
        )
        cursor_store.save(source_name)

    write_csv(
        data_root / "reporting" / "pipeline_metrics.csv",
        metrics,
        ["source", "records", "valid_records", "invalid_records"],
    )
    customer_health = build_customer_health(data_root)
    return build_dashboard(data_root, customer_health, metrics)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config/demo_sources.json")
    parser.add_argument("--schemas", default="config/schemas.json")
    parser.add_argument("--data-root", default="data")
    args = parser.parse_args()
    dashboard = run_pipeline(Path(args.config), Path(args.schemas), Path(args.data_root))
    print(f"Demo pipeline complete. Open {dashboard}")


if __name__ == "__main__":
    main()
