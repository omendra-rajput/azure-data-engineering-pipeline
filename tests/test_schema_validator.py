from src.quality.schema_validator import validate_record


def test_validate_record_accepts_required_fields() -> None:
    schema = {
        "required": ["id", "amount"],
        "types": {"id": "string", "amount": "integer"},
    }

    result = validate_record({"id": "ch_123", "amount": 1000}, schema)

    assert result.valid
    assert result.errors == []


def test_validate_record_reports_missing_and_type_errors() -> None:
    schema = {
        "required": ["id", "amount"],
        "types": {"id": "string", "amount": "integer"},
    }

    result = validate_record({"id": 123}, schema)

    assert not result.valid
    assert "Missing required field: amount" in result.errors
    assert "id expected string" in result.errors
