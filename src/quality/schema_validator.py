from __future__ import annotations

from dataclasses import dataclass
from typing import Any


TYPE_MAP = {
    "string": str,
    "integer": int,
    "object": dict,
}


@dataclass(frozen=True)
class SchemaResult:
    valid: bool
    errors: list[str]


def validate_record(record: dict[str, Any], schema: dict[str, Any]) -> SchemaResult:
    errors: list[str] = []

    for field in schema.get("required", []):
        if field not in record or record[field] is None:
            errors.append(f"Missing required field: {field}")

    for field, expected_type in schema.get("types", {}).items():
        if field not in record or record[field] is None:
            continue
        if expected_type == "timestamp":
            if not isinstance(record[field], str):
                errors.append(f"{field} expected timestamp string")
            continue
        python_type = TYPE_MAP.get(expected_type)
        if python_type and not isinstance(record[field], python_type):
            errors.append(f"{field} expected {expected_type}")

    return SchemaResult(valid=not errors, errors=errors)
