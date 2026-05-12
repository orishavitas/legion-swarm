"""Probe a repo for git state + Nexus harness state. Pure, never raises."""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class RepoSnapshot:
    name: str
    path: Path
    branch: str = ""
    dirty: bool = False
    ahead: int = 0
    behind: int = 0
    last_commit_age: str = "—"
    is_nexus: bool = False
    active_task: str = ""
    phase_status: str = ""
    error: str = ""


_PHASE_RE = re.compile(r"Active phase\s*:\s*(.+)", re.IGNORECASE)


def _run_git(repo: Path, *args: str, timeout: float = 5.0) -> str:
    res = subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    if res.returncode != 0:
        raise RuntimeError(res.stderr.strip() or f"git {' '.join(args)} failed")
    return res.stdout.strip()


def _humanize_age(seconds: float) -> str:
    s = int(seconds)
    if s < 60:
        return f"{s}s"
    if s < 3600:
        return f"{s // 60}m"
    if s < 86400:
        return f"{s // 3600}h"
    return f"{s // 86400}d"


def _read_active_task(harness: Path) -> str:
    inbox = harness / "inbox"
    if not inbox.is_dir():
        return ""
    candidates = sorted(
        (p for p in inbox.glob("*.task.md") if p.is_file()),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if not candidates:
        return ""
    return candidates[0].name.removesuffix(".task.md")


def _read_phase_status(repo: Path) -> str:
    claude_md = repo / "CLAUDE.md"
    if not claude_md.is_file():
        return ""
    try:
        text = claude_md.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    m = _PHASE_RE.search(text)
    return m.group(1).strip() if m else ""


def scan_repo(path: Path) -> RepoSnapshot:
    path = Path(path)
    snap = RepoSnapshot(name=path.name, path=path)
    if not path.is_dir():
        snap.error = "not a directory"
        return snap
    if not (path / ".git").exists():
        snap.error = "not a git repo"
        return snap
    try:
        snap.branch = _run_git(path, "rev-parse", "--abbrev-ref", "HEAD") or "(detached)"
        snap.dirty = bool(_run_git(path, "status", "--porcelain"))
        try:
            ab = _run_git(path, "rev-list", "--left-right", "--count", "@{u}...HEAD")
            behind_str, ahead_str = ab.split()
            snap.ahead = int(ahead_str)
            snap.behind = int(behind_str)
        except RuntimeError:
            pass
        ts_str = _run_git(path, "log", "-1", "--format=%ct")
        if ts_str:
            age = (
                datetime.now(timezone.utc)
                - datetime.fromtimestamp(int(ts_str), tz=timezone.utc)
            ).total_seconds()
            snap.last_commit_age = _humanize_age(age)
        harness = path / ".agent-harness"
        snap.is_nexus = harness.is_dir()
        if snap.is_nexus:
            snap.active_task = _read_active_task(harness)
        snap.phase_status = _read_phase_status(path)
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
        snap.error = str(exc)
    return snap
