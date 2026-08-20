from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests
from tenacity import retry, stop_after_attempt, wait_exponential

from src.ingestion.cursor_store import CursorStore


def build_incremental_params(incremental_field: str, cursor_value: str) -> dict[str, str]:
    return {f"{incremental_field}_gte": cursor_value}


@retry(wait=wait_exponential(multiplier=1, min=2, max=30), stop=stop_after_attempt(5))
def fetch_page(endpoint: str, headers: dict[str, str], params: dict[str, str]) -> dict[str, Any]:
    response = requests.get(endpoint, headers=headers, params=params, timeout=45)
    response.raise_for_status()
    return response.json()


def write_landing_file(source_name: str, rows: list[dict[str, Any]], output_root: Path) -> Path:
    load_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    output_dir = output_root / source_name / f"load_date={load_date}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "part-00000.jsonl"
    with output_file.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=True) + "\n")
    return output_file


def run_source(source_name: str, dry_run: bool) -> Path:
    cursor_store = CursorStore(Path(".state/cursors.json"))
    cursor_value = cursor_store.load(source_name)

    if dry_run:
        rows = [
            {
                "id": "dry-run-1",
                "source": source_name,
                "updated_at": cursor_value,
                "_ingested_at": datetime.now(timezone.utc).isoformat(),
            }
        ]
    else:
        endpoint = os.environ[f"{source_name.upper()}_ENDPOINT"]
        token = os.environ[f"{source_name.upper()}_TOKEN"]
        rows = fetch_page(
            endpoint,
            headers={"Authorization": f"Bearer {token}"},
            params=build_incremental_params("updated_at", cursor_value),
        ).get("data", [])

    output_file = write_landing_file(source_name, rows, Path("data/raw"))
    cursor_store.save(source_name)
    return output_file


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    output_file = run_source(args.source, args.dry_run)
    print(f"Wrote {output_file}")


if __name__ == "__main__":
    main()
