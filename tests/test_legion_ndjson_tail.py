import json
from pathlib import Path

from legion.ndjson_tail import MultiTailer


def _append(p: Path, obj: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(obj) + "\n")


def test_first_poll_reads_existing_lines(tmp_path):
    log = tmp_path / "a" / "monitor.ndjson"
    _append(log, {"event": "start", "task_id": "T1"})
    _append(log, {"event": "ok", "task_id": "T1"})
    t = MultiTailer({"alpha": log})
    events = t.poll()
    assert len(events) == 2
    assert events[0]["repo"] == "alpha"
    assert events[1]["event"] == "ok"


def test_subsequent_poll_returns_only_new(tmp_path):
    log = tmp_path / "monitor.ndjson"
    _append(log, {"event": "a", "task_id": "T1"})
    t = MultiTailer({"r": log})
    t.poll()
    _append(log, {"event": "b", "task_id": "T2"})
    new = t.poll()
    assert len(new) == 1
    assert new[0]["event"] == "b"


def test_missing_file_is_skipped(tmp_path):
    t = MultiTailer({"missing": tmp_path / "nope.ndjson"})
    assert t.poll() == []


def test_truncation_resets_offset(tmp_path):
    log = tmp_path / "monitor.ndjson"
    _append(log, {"event": "a", "task_id": "T"})
    _append(log, {"event": "b", "task_id": "T"})
    t = MultiTailer({"r": log})
    t.poll()
    log.write_text("", encoding="utf-8")
    _append(log, {"event": "c", "task_id": "T"})
    new = t.poll()
    assert [e["event"] for e in new] == ["c"]


def test_malformed_line_is_skipped_not_raised(tmp_path):
    log = tmp_path / "monitor.ndjson"
    log.parent.mkdir(parents=True, exist_ok=True)
    log.write_text("not json\n" + json.dumps({"event": "ok", "task_id": "T"}) + "\n", encoding="utf-8")
    t = MultiTailer({"r": log})
    events = t.poll()
    assert len(events) == 1
    assert events[0]["event"] == "ok"
