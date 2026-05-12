"""v1 command-bar actions. Local only — no network beyond plain git push."""

from __future__ import annotations

import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path

_TASK_ID_RE = re.compile(r"^[A-Za-z0-9_\-.]+$")


@dataclass
class CommandResult:
    ok: bool
    message: str


def drop_packet(repo: Path, task_id: str, body: str) -> CommandResult:
    repo = Path(repo)
    if not _TASK_ID_RE.match(task_id):
        return CommandResult(False, f"invalid task_id: {task_id!r}")
    inbox = repo / ".agent-harness" / "inbox"
    if not inbox.is_dir():
        return CommandResult(False, f"inbox missing: {inbox}")
    target = inbox / f"{task_id}.task.md"
    if target.exists():
        return CommandResult(False, f"refusing to overwrite {target.name}")
    try:
        target.write_text(body, encoding="utf-8")
    except OSError as exc:
        return CommandResult(False, f"write failed: {exc}")
    return CommandResult(True, f"dropped {target}")


def open_claude_md(repo: Path, editor: str = "code") -> CommandResult:
    repo = Path(repo)
    target = repo / "CLAUDE.md"
    if not target.is_file():
        return CommandResult(False, f"no CLAUDE.md in {repo}")
    cmd = shlex.split(editor) + [str(target)]
    try:
        subprocess.Popen(cmd, cwd=repo)
    except (OSError, FileNotFoundError) as exc:
        return CommandResult(False, f"editor launch failed: {exc}")
    return CommandResult(True, f"opened {target}")


def git_push(repo: Path) -> CommandResult:
    repo = Path(repo)
    res = subprocess.run(
        ["git", "push"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if res.returncode != 0:
        return CommandResult(False, (res.stderr or res.stdout).strip()[:400])
    return CommandResult(True, (res.stdout or res.stderr).strip()[:400])
