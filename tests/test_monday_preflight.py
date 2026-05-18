from datetime import datetime, timezone
from pathlib import Path

from legion.monday_preflight import (
    MondayPreflight,
    load_monday_preflight,
    preflight_path,
    record_monday_preflight,
)


def test_record_monday_preflight_writes_durable_missing_status(tmp_path):
    generated_at = datetime(2026, 5, 18, 12, 0, 0, tzinfo=timezone.utc)

    result = record_monday_preflight(
        tmp_path,
        MondayPreflight(
            repo="legion-swarm",
            board_id="18408420731",
            status="missing",
            evidence="Monday MCP write tool was not exposed in this session.",
            generated_at=generated_at,
        ),
    )

    assert result == preflight_path(tmp_path)
    text = result.read_text(encoding="utf-8")
    assert "Status: missing" in text
    assert "Board ID: 18408420731" in text
    assert "Monday MCP write tool was not exposed" in text


def test_load_monday_preflight_round_trips_status(tmp_path):
    generated_at = datetime(2026, 5, 18, 12, 0, 0, tzinfo=timezone.utc)
    record_monday_preflight(
        tmp_path,
        MondayPreflight(
            repo="legion-swarm",
            board_id="18408420731",
            status="available",
            evidence="create_update and change_item_column_values are callable.",
            generated_at=generated_at,
        ),
    )

    loaded = load_monday_preflight(tmp_path)

    assert loaded == MondayPreflight(
        repo="legion-swarm",
        board_id="18408420731",
        status="available",
        evidence="create_update and change_item_column_values are callable.",
        generated_at=generated_at,
    )


def test_load_monday_preflight_returns_none_when_missing(tmp_path):
    assert load_monday_preflight(tmp_path) is None
