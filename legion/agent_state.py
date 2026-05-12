"""Read agent status: Claude state file + Codex inbox snapshots."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, List, Tuple

STALE_AFTER_SECONDS = 300


@dataclass
class ClaudeState:
    present: bool = False
    context_pct_used: int | None = None
    model: str = ""
    current_repo: str = ""
    last_updated: str = ""
    stale: bool = False


def read_claude(path: Path | None) -> ClaudeState:
    if path is None or not Path(path).is_file():
        return ClaudeState()
    try:
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ClaudeState()
    state = ClaudeState(
        present=True,
        context_pct_used=raw.get("context_pct_used"),
        model=raw.get("model", ""),
        current_repo=raw.get("current_repo", ""),
        last_updated=raw.get("last_updated", ""),
    )
    if state.last_updated:
        try:
            ts = datetime.fromisoformat(state.last_updated)
            state.stale = (datetime.now(timezone.utc) - ts).total_seconds() > STALE_AFTER_SECONDS
        except ValueError:
            state.stale = True
    return state


def codex_active(repo_paths: Iterable[Path]) -> List[Tuple[str, str]]:
    out: List[Tuple[str, str]] = []
    for repo in repo_paths:
        inbox = Path(repo) / ".agent-harness" / "inbox"
        if not inbox.is_dir():
            continue
        for f in sorted(inbox.glob("*.task.md")):
            out.append((Path(repo).name, f.name.removesuffix(".task.md")))
    return out
