import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from legion import agent_state


def test_read_claude_missing_returns_empty(tmp_path):
    s = agent_state.read_claude(tmp_path / "nope.json")
    assert s.present is False


def test_read_claude_fresh(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({
        "context_pct_used": 33,
        "current_repo": "demo",
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }), encoding="utf-8")
    s = agent_state.read_claude(p)
    assert s.present is True
    assert s.context_pct_used == 33
    assert s.stale is False


def test_read_claude_stale(tmp_path):
    p = tmp_path / "c.json"
    old = (datetime.now(timezone.utc) - timedelta(minutes=30)).isoformat()
    p.write_text(json.dumps({"context_pct_used": 50, "last_updated": old}), encoding="utf-8")
    s = agent_state.read_claude(p)
    assert s.stale is True


def test_codex_active_lists_inbox(tmp_path):
    repo = tmp_path / "r"
    inbox = repo / ".agent-harness" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "TASK-1.task.md").write_text("# Task Packet: TASK-1", encoding="utf-8")
    (inbox / "TASK-2.task.md").write_text("# Task Packet: TASK-2", encoding="utf-8")
    found = agent_state.codex_active([repo])
    assert ("r", "TASK-1") in found and ("r", "TASK-2") in found
