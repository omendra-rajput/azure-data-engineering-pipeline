from pathlib import Path

from src.ingestion.cursor_store import CursorStore


def test_cursor_store_defaults_to_epoch(tmp_path: Path) -> None:
    store = CursorStore(tmp_path / "cursors.json")

    assert store.load("missing_source") == "1970-01-01T00:00:00Z"


def test_cursor_store_saves_source_cursor(tmp_path: Path) -> None:
    store = CursorStore(tmp_path / "cursors.json")

    store.save("stripe_charges", "2026-08-20T00:00:00Z")

    assert store.load("stripe_charges") == "2026-08-20T00:00:00Z"
