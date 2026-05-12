# Legion Nerve Center — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a read-only live TUI dashboard that gives the operator a single pane of glass over all repos under `C:/Users/OriShavit/Documents/GitHub/`.

**Architecture:** A `legion/` Python package with a Rich Live TUI entry point. Reads local filesystem only (no API calls in v1). Four panels: Repo Grid, Activity Feed, Agent Status, Command Bar. Repo scanning runs in a thread pool to avoid UI blocking.

**Tech Stack:** Python 3.11+, `rich>=13.7`, `pytest>=8.0`, stdlib only otherwise (`subprocess`, `pathlib`, `json`, `threading`).

---

## File Structure

```
legion/
  __init__.py              # package init, __version__
  __main__.py              # python -m legion entry
  nerve_center.py          # TUI entry point, Rich Live loop, layout
  config.py                # load + validate legion/config.json
  repo_scan.py             # per-repo git + harness probe (pure functions)
  ndjson_tail.py           # multi-file NDJSON tailer (stateful, polling)
  agent_state.py           # read claude state file + codex inbox
  commands.py              # v1 command bar actions
  config.json              # operator-edited repo list + settings
  README.md                # how to run
  requirements.txt         # rich, pytest
  state/                   # gitignored — operator-local runtime state

tests/
  test_legion_config.py
  test_legion_repo_scan.py
  test_legion_ndjson_tail.py
  test_legion_agent_state.py
  test_legion_commands.py
  test_legion_nerve_center_smoke.py
```

### Data contracts

**`legion/config.json`:**
```json
{
  "repos_root": "C:/Users/OriShavit/Documents/GitHub",
  "repos": [],
  "refresh_seconds": 30,
  "feed_max_lines": 200,
  "claude_state_file": "C:/Users/OriShavit/Documents/GitHub/project_nexus/project-nexus/legion/state/claude.json",
  "editor": "code"
}
```
`repos: []` = auto-discover every `.git/` dir under `repos_root`.

**`legion/state/claude.json`** (operator writes, Nerve Center reads):
```json
{
  "context_pct_used": 47,
  "model": "claude-sonnet-4-6",
  "current_repo": "file-management-agent",
  "last_updated": "2026-05-05T09:12:00+00:00"
}
```
Stale threshold: `last_updated` older than 5 minutes → shown as `(stale)`.

---

### Task 1: Scaffold `legion/` package and requirements

**Files:**
- Create: `legion/__init__.py`
- Create: `legion/requirements.txt`
- Create: `legion/README.md`
- Modify: `.gitignore`

- [ ] **Step 1.1: Create `legion/__init__.py`**

```python
"""Legion Nerve Center — cross-repo live TUI dashboard. v1 read-only."""

__version__ = "0.1.0"
```

- [ ] **Step 1.2: Create `legion/requirements.txt`**

```
rich>=13.7
pytest>=8.0
```

- [ ] **Step 1.3: Create `legion/README.md`**

```markdown
# Legion Nerve Center

Cross-repo live TUI dashboard for the Nexus methodology.

## Run

```powershell
pip install -r legion/requirements.txt
python -m legion
```

## Config

Edit `legion/config.json`:
- `repos_root` — folder containing all repos
- `repos` — list of repo paths relative to `repos_root`. Empty = auto-discover.
- `refresh_seconds` — repo grid refresh interval (default 30)
- `claude_state_file` — path Claude writes its state to (optional)
- `editor` — command to open files (default `code`)

## Keys

`q` quit | `r` force refresh | `p` push repo | `e` edit CLAUDE.md | `t` drop task packet
```

- [ ] **Step 1.4: Append to `.gitignore`**

```
# Legion Nerve Center local state
legion/state/
```

- [ ] **Step 1.5: Verify**

```powershell
python -c "import legion; print(legion.__version__)"
```
Expected: `0.1.0`

- [ ] **Step 1.6: Commit**

```bash
git add legion/__init__.py legion/requirements.txt legion/README.md .gitignore
git commit -m "legion: scaffold package and requirements"
```

---

### Task 2: Config loader (TDD)

**Files:**
- Create: `legion/config.py`
- Create: `tests/test_legion_config.py`
- Create: `legion/config.json`

- [ ] **Step 2.1: Write failing tests**

Create `tests/test_legion_config.py`:
```python
import json
from pathlib import Path

import pytest

from legion import config as legion_config


def _write(path: Path, data: dict) -> Path:
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_load_minimal(tmp_path):
    repos_root = tmp_path / "ghub"
    (repos_root / "a").mkdir(parents=True)
    cfg_path = _write(tmp_path / "c.json", {
        "repos_root": str(repos_root),
        "repos": ["a"],
    })
    cfg = legion_config.load_config(cfg_path)
    assert cfg.repos_root == repos_root
    assert cfg.repo_paths == [repos_root / "a"]
    assert cfg.refresh_seconds == 30
    assert cfg.feed_max_lines == 200
    assert cfg.editor == "code"


def test_autodiscover_when_repos_empty(tmp_path):
    root = tmp_path / "g"
    (root / "alpha" / ".git").mkdir(parents=True)
    (root / "beta" / ".git").mkdir(parents=True)
    (root / "gamma").mkdir(parents=True)  # no .git, must be skipped
    cfg_path = _write(tmp_path / "c.json", {
        "repos_root": str(root),
        "repos": [],
    })
    cfg = legion_config.load_config(cfg_path)
    names = sorted(p.name for p in cfg.repo_paths)
    assert names == ["alpha", "beta"]


def test_missing_repos_root_raises(tmp_path):
    cfg_path = _write(tmp_path / "c.json", {
        "repos_root": str(tmp_path / "does-not-exist"),
        "repos": [],
    })
    with pytest.raises(legion_config.ConfigError):
        legion_config.load_config(cfg_path)


def test_missing_file_raises(tmp_path):
    with pytest.raises(legion_config.ConfigError):
        legion_config.load_config(tmp_path / "nope.json")


def test_missing_repo_path_recorded(tmp_path):
    root = tmp_path / "g"
    root.mkdir()
    cfg_path = _write(tmp_path / "c.json", {
        "repos_root": str(root),
        "repos": ["ghost"],
    })
    cfg = legion_config.load_config(cfg_path)
    assert cfg.repo_paths == [root / "ghost"]
```

- [ ] **Step 2.2: Run tests, confirm failure**

```powershell
python -m pytest tests/test_legion_config.py -x
```
Expected: `ModuleNotFoundError: No module named 'legion.config'`

- [ ] **Step 2.3: Implement `legion/config.py`**

```python
"""Load and validate legion/config.json."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List


class ConfigError(Exception):
    pass


@dataclass
class Config:
    repos_root: Path
    repo_paths: List[Path] = field(default_factory=list)
    refresh_seconds: int = 30
    feed_max_lines: int = 200
    claude_state_file: Path | None = None
    editor: str = "code"


def _autodiscover(root: Path) -> List[Path]:
    return sorted(
        child for child in root.iterdir()
        if child.is_dir() and (child / ".git").exists()
    )


def load_config(path: Path) -> Config:
    path = Path(path)
    if not path.exists():
        raise ConfigError(f"config not found: {path}")
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc}") from exc

    repos_root = Path(raw.get("repos_root", "")).resolve()
    if not repos_root.is_dir():
        raise ConfigError(f"repos_root does not exist: {repos_root}")

    repo_list = raw.get("repos", [])
    repo_paths = (
        [(repos_root / r).resolve() for r in repo_list]
        if repo_list
        else _autodiscover(repos_root)
    )

    claude_state_file = raw.get("claude_state_file")
    return Config(
        repos_root=repos_root,
        repo_paths=repo_paths,
        refresh_seconds=int(raw.get("refresh_seconds", 30)),
        feed_max_lines=int(raw.get("feed_max_lines", 200)),
        claude_state_file=Path(claude_state_file).resolve() if claude_state_file else None,
        editor=raw.get("editor", "code"),
    )
```

- [ ] **Step 2.4: Verify**

```powershell
python -m pytest tests/test_legion_config.py -v
```
Expected: 5 passed

- [ ] **Step 2.5: Create `legion/config.json`**

```json
{
  "repos_root": "C:/Users/OriShavit/Documents/GitHub",
  "repos": [],
  "refresh_seconds": 30,
  "feed_max_lines": 200,
  "claude_state_file": "C:/Users/OriShavit/Documents/GitHub/project_nexus/project-nexus/legion/state/claude.json",
  "editor": "code"
}
```

- [ ] **Step 2.6: Commit**

```bash
git add legion/config.py legion/config.json tests/test_legion_config.py
git commit -m "legion: config loader with validation and autodiscovery"
```

---

### Task 3: Repo scanner (TDD)

**Files:**
- Create: `legion/repo_scan.py`
- Create: `tests/test_legion_repo_scan.py`

- [ ] **Step 3.1: Write failing tests**

Create `tests/test_legion_repo_scan.py`:
```python
import subprocess
from pathlib import Path

from legion import repo_scan


def _git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def _init_repo(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    _git(path, "init", "-q", "-b", "main")
    _git(path, "config", "user.email", "t@t.t")
    _git(path, "config", "user.name", "t")
    (path / "f.txt").write_text("hi", encoding="utf-8")
    _git(path, "add", ".")
    _git(path, "commit", "-q", "-m", "init")
    return path


def test_scan_basic(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    snap = repo_scan.scan_repo(repo)
    assert snap.name == "demo"
    assert snap.branch == "main"
    assert snap.dirty is False
    assert snap.ahead == 0
    assert snap.behind == 0
    assert snap.is_nexus is False
    assert snap.active_task == ""
    assert snap.error == ""


def test_scan_dirty(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    (repo / "f.txt").write_text("changed", encoding="utf-8")
    snap = repo_scan.scan_repo(repo)
    assert snap.dirty is True


def test_scan_nexus_with_active_task(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    inbox = repo / ".agent-harness" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "TASK-42.task.md").write_text("# Task Packet: TASK-42\n", encoding="utf-8")
    snap = repo_scan.scan_repo(repo)
    assert snap.is_nexus is True
    assert snap.active_task == "TASK-42"


def test_scan_phase_status_from_claude_md(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    (repo / "CLAUDE.md").write_text(
        "# CLAUDE.md\n\nActive phase: Phase 7 — Nerve Center build\nmore text\n",
        encoding="utf-8",
    )
    snap = repo_scan.scan_repo(repo)
    assert "Phase 7" in snap.phase_status


def test_scan_missing_repo_records_error(tmp_path):
    snap = repo_scan.scan_repo(tmp_path / "nope")
    assert snap.error != ""
    assert snap.name == "nope"


def test_scan_non_git_directory_records_error(tmp_path):
    p = tmp_path / "plain"
    p.mkdir()
    snap = repo_scan.scan_repo(p)
    assert snap.error != ""


def test_last_commit_age_format(tmp_path):
    repo = _init_repo(tmp_path / "demo")
    snap = repo_scan.scan_repo(repo)
    assert snap.last_commit_age and " " not in snap.last_commit_age
```

- [ ] **Step 3.2: Run, confirm failure**

```powershell
python -m pytest tests/test_legion_repo_scan.py -x
```
Expected: `ModuleNotFoundError`

- [ ] **Step 3.3: Implement `legion/repo_scan.py`**

```python
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
            age = (datetime.now(timezone.utc) - datetime.fromtimestamp(int(ts_str), tz=timezone.utc)).total_seconds()
            snap.last_commit_age = _humanize_age(age)
        harness = path / ".agent-harness"
        snap.is_nexus = harness.is_dir()
        if snap.is_nexus:
            snap.active_task = _read_active_task(harness)
        snap.phase_status = _read_phase_status(path)
    except (RuntimeError, subprocess.TimeoutExpired, OSError) as exc:
        snap.error = str(exc)
    return snap
```

- [ ] **Step 3.4: Verify**

```powershell
python -m pytest tests/test_legion_repo_scan.py -v
```
Expected: 7 passed

- [ ] **Step 3.5: Commit**

```bash
git add legion/repo_scan.py tests/test_legion_repo_scan.py
git commit -m "legion: repo_scan probe for git + harness state"
```

---

### Task 4: Multi-file NDJSON tailer (TDD)

**Files:**
- Create: `legion/ndjson_tail.py`
- Create: `tests/test_legion_ndjson_tail.py`

- [ ] **Step 4.1: Write failing tests**

Create `tests/test_legion_ndjson_tail.py`:
```python
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
```

- [ ] **Step 4.2: Run, confirm failure**

```powershell
python -m pytest tests/test_legion_ndjson_tail.py -x
```

- [ ] **Step 4.3: Implement `legion/ndjson_tail.py`**

```python
"""Polling tailer for multiple NDJSON files. Stateful, keeps byte offsets."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Mapping


class MultiTailer:
    def __init__(self, sources: Mapping[str, Path]) -> None:
        self._sources: Dict[str, Path] = {k: Path(v) for k, v in sources.items()}
        self._offsets: Dict[str, int] = {k: 0 for k in self._sources}

    def poll(self) -> List[dict]:
        events: List[dict] = []
        for name, path in self._sources.items():
            events.extend(self._poll_one(name, path))
        return events

    def _poll_one(self, name: str, path: Path) -> List[dict]:
        if not path.is_file():
            return []
        try:
            size = path.stat().st_size
        except OSError:
            return []
        offset = self._offsets.get(name, 0)
        if size < offset:
            offset = 0
        if size == offset:
            return []
        try:
            with path.open("rb") as f:
                f.seek(offset)
                chunk = f.read(size - offset)
        except OSError:
            return []
        self._offsets[name] = size
        out: List[dict] = []
        for raw in chunk.splitlines():
            if not raw.strip():
                continue
            try:
                obj = json.loads(raw.decode("utf-8", errors="replace"))
            except json.JSONDecodeError:
                continue
            obj["repo"] = name
            out.append(obj)
        return out
```

- [ ] **Step 4.4: Verify**

```powershell
python -m pytest tests/test_legion_ndjson_tail.py -v
```
Expected: 5 passed

- [ ] **Step 4.5: Commit**

```bash
git add legion/ndjson_tail.py tests/test_legion_ndjson_tail.py
git commit -m "legion: multi-file NDJSON tailer"
```

---

### Task 5: Agent state reader (TDD)

**Files:**
- Create: `legion/agent_state.py`
- Create: `tests/test_legion_agent_state.py`

- [ ] **Step 5.1: Write failing tests**

Create `tests/test_legion_agent_state.py`:
```python
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
```

- [ ] **Step 5.2: Run, confirm failure**

```powershell
python -m pytest tests/test_legion_agent_state.py -x
```

- [ ] **Step 5.3: Implement `legion/agent_state.py`**

```python
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
```

- [ ] **Step 5.4: Verify**

```powershell
python -m pytest tests/test_legion_agent_state.py -v
```
Expected: 4 passed

- [ ] **Step 5.5: Commit**

```bash
git add legion/agent_state.py tests/test_legion_agent_state.py
git commit -m "legion: agent_state reader for Claude + Codex"
```

---

### Task 6: Command actions (TDD)

**Files:**
- Create: `legion/commands.py`
- Create: `tests/test_legion_commands.py`

- [ ] **Step 6.1: Write failing tests**

Create `tests/test_legion_commands.py`:
```python
import subprocess
from pathlib import Path

from legion import commands


def _init_repo(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=p, check=True)
    return p


def test_drop_packet_writes_file(tmp_path):
    repo = _init_repo(tmp_path / "r")
    (repo / ".agent-harness" / "inbox").mkdir(parents=True)
    res = commands.drop_packet(repo, "TASK-9", "# Task Packet: TASK-9\nbody\n")
    assert res.ok
    assert (repo / ".agent-harness" / "inbox" / "TASK-9.task.md").exists()


def test_drop_packet_rejects_bad_id(tmp_path):
    repo = _init_repo(tmp_path / "r")
    (repo / ".agent-harness" / "inbox").mkdir(parents=True)
    res = commands.drop_packet(repo, "bad id with spaces", "x")
    assert not res.ok


def test_drop_packet_no_inbox(tmp_path):
    repo = _init_repo(tmp_path / "r")
    res = commands.drop_packet(repo, "TASK-1", "x")
    assert not res.ok
    assert "inbox" in res.message.lower()


def test_drop_packet_refuses_overwrite(tmp_path):
    repo = _init_repo(tmp_path / "r")
    inbox = repo / ".agent-harness" / "inbox"
    inbox.mkdir(parents=True)
    (inbox / "TASK-1.task.md").write_text("existing", encoding="utf-8")
    res = commands.drop_packet(repo, "TASK-1", "new")
    assert not res.ok


def test_open_claude_md_missing(tmp_path):
    repo = _init_repo(tmp_path / "r")
    res = commands.open_claude_md(repo, editor="echo")
    assert not res.ok


def test_git_push_no_remote(tmp_path):
    repo = _init_repo(tmp_path / "r")
    (repo / "f.txt").write_text("x", encoding="utf-8")
    subprocess.run(["git", "-C", str(repo), "config", "user.email", "t@t.t"], check=True)
    subprocess.run(["git", "-C", str(repo), "config", "user.name", "t"], check=True)
    subprocess.run(["git", "-C", str(repo), "add", "."], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-q", "-m", "x"], check=True)
    res = commands.git_push(repo)
    assert not res.ok
```

- [ ] **Step 6.2: Run, confirm failure**

```powershell
python -m pytest tests/test_legion_commands.py -x
```

- [ ] **Step 6.3: Implement `legion/commands.py`**

```python
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
```

- [ ] **Step 6.4: Verify**

```powershell
python -m pytest tests/test_legion_commands.py -v
```
Expected: 6 passed

- [ ] **Step 6.5: Commit**

```bash
git add legion/commands.py tests/test_legion_commands.py
git commit -m "legion: command actions (drop_packet, git_push, open_claude_md)"
```

---

### Task 7: TUI entry point with Rich Live

**Files:**
- Create: `legion/nerve_center.py`
- Create: `tests/test_legion_nerve_center_smoke.py`

- [ ] **Step 7.1: Write smoke test**

Create `tests/test_legion_nerve_center_smoke.py`:
```python
import importlib


def test_module_imports():
    mod = importlib.import_module("legion.nerve_center")
    assert hasattr(mod, "main")
    assert hasattr(mod, "build_layout")
```

- [ ] **Step 7.2: Implement `legion/nerve_center.py`**

```python
"""Legion Nerve Center — read-only live TUI dashboard. v1."""

from __future__ import annotations

import argparse
import sys
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Deque, List

from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from legion import agent_state, commands, ndjson_tail, repo_scan
from legion.config import Config, ConfigError, load_config


DEFAULT_CONFIG = Path(__file__).parent / "config.json"


def _read_key_nonblocking() -> str | None:
    try:
        import msvcrt  # type: ignore[import-not-found]
    except ImportError:
        return None
    if msvcrt.kbhit():
        return msvcrt.getwch()
    return None


def _repo_grid(snapshots: List[repo_scan.RepoSnapshot]) -> Panel:
    table = Table(expand=True, show_lines=False, header_style="bold magenta")
    table.add_column("Repo", style="bold", no_wrap=True)
    table.add_column("Branch", no_wrap=True)
    table.add_column("Δ", justify="center")
    table.add_column("↑/↓", justify="right")
    table.add_column("Age", justify="right")
    table.add_column("Nx", justify="center")
    table.add_column("Active Task", no_wrap=True)
    table.add_column("Phase", overflow="fold")

    for s in snapshots:
        if s.error:
            table.add_row(s.name, Text(f"err: {s.error[:40]}", style="red"), "", "", "", "", "", "")
            continue
        dirty = Text("●", style="yellow") if s.dirty else Text("·", style="dim")
        ab_style = "red" if s.behind else ("green" if s.ahead else "dim")
        nexus = Text("N", style="cyan") if s.is_nexus else Text("·", style="dim")
        active = Text(s.active_task, style="cyan bold") if s.active_task else Text("—", style="dim")
        table.add_row(
            s.name, s.branch, dirty,
            Text(f"{s.ahead}/{s.behind}", style=ab_style),
            s.last_commit_age, nexus, active,
            Text(s.phase_status, style="dim"),
        )
    return Panel(table, title="[bold]Repo Grid[/]", border_style="magenta")


def _feed_panel(events: Deque[dict]) -> Panel:
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(no_wrap=True, style="dim")
    table.add_column(no_wrap=True, style="cyan")
    table.add_column(no_wrap=True)
    table.add_column(no_wrap=True)
    table.add_column(overflow="fold")
    for e in list(events):
        ts = e.get("ts", "")[11:19]
        ev = e.get("event", "")
        ev_style = "green" if "pass" in ev or "ok" in ev else ("red" if "fail" in ev or "error" in ev else "white")
        table.add_row(ts, e.get("repo", ""), Text(ev, style=ev_style), e.get("task_id", ""), e.get("message", ""))
    return Panel(table, title="[bold]Activity Feed[/]", border_style="cyan")


def _agent_panel(claude: agent_state.ClaudeState, codex: list) -> Panel:
    table = Table.grid(expand=True, padding=(0, 1))
    table.add_column(style="bold")
    table.add_column(overflow="fold")
    if not claude.present:
        table.add_row("Claude", Text("no state file", style="dim"))
    else:
        pct = claude.context_pct_used or 0
        ctx_style = "red" if pct > 75 else ("yellow" if pct > 50 else "green")
        label = f"{pct}%" + (" (stale)" if claude.stale else "")
        table.add_row("Claude ctx", Text(label, style=ctx_style))
        if claude.current_repo:
            table.add_row("Claude repo", claude.current_repo)
        if claude.model:
            table.add_row("model", Text(claude.model, style="dim"))
    if codex:
        for repo_name, task_id in codex:
            table.add_row(f"Codex@{repo_name}", Text(task_id, style="cyan"))
    else:
        table.add_row("Codex", Text("idle", style="dim"))
    return Panel(table, title="[bold]Agents[/]", border_style="green")


def _command_panel(last_result: str, last_refresh: datetime) -> Panel:
    body = Text.from_markup(
        "[bold]q[/] quit  [bold]r[/] refresh  [bold]p[/] push  [bold]e[/] edit CLAUDE.md  [bold]t[/] drop packet\n"
        f"[dim]refreshed: {last_refresh:%H:%M:%S}  last: {last_result or '—'}[/]"
    )
    return Panel(body, title="[bold]Commands[/]", border_style="yellow")


def build_layout() -> Layout:
    root = Layout(name="root")
    root.split_column(Layout(name="top"), Layout(name="bottom", size=6))
    root["top"].split_row(Layout(name="grid", ratio=2), Layout(name="side", ratio=1))
    root["side"].split_column(Layout(name="agents", size=10), Layout(name="feed"))
    root["bottom"].update(Panel(""))
    return root


def _scan_all(paths: list[Path]) -> list[repo_scan.RepoSnapshot]:
    snaps: list[repo_scan.RepoSnapshot | None] = [None] * len(paths)
    with ThreadPoolExecutor(max_workers=8) as pool:
        futs = {pool.submit(repo_scan.scan_repo, p): i for i, p in enumerate(paths)}
        for fut in as_completed(futs):
            snaps[futs[fut]] = fut.result()
    return [s for s in snaps if s is not None]


def _prompt(console: Console, question: str) -> str:
    console.print(question, end=" ", style="bold yellow")
    try:
        return input().strip()
    except EOFError:
        return ""


def _pick_repo(console: Console, cfg: Config) -> Path | None:
    name = _prompt(console, "repo name (Enter to cancel):")
    if not name:
        return None
    for p in cfg.repo_paths:
        if p.name == name:
            return p
    console.print(f"[red]no repo named {name!r}[/]")
    return None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="legion-nerve-center")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    args = parser.parse_args(argv)

    try:
        cfg = load_config(args.config)
    except ConfigError as exc:
        print(f"config error: {exc}", file=sys.stderr)
        return 2

    console = Console()
    layout = build_layout()
    feed: Deque[dict] = deque(maxlen=cfg.feed_max_lines)
    tailer = ndjson_tail.MultiTailer({
        p.name: p / ".agent-harness" / "logs" / "monitor.ndjson"
        for p in cfg.repo_paths
    })

    last_scan = 0.0
    last_result = ""
    snapshots: list[repo_scan.RepoSnapshot] = []
    last_refresh = datetime.now(timezone.utc)

    with Live(layout, console=console, refresh_per_second=4, screen=True) as live:
        while True:
            now = time.monotonic()
            if now - last_scan >= cfg.refresh_seconds or not snapshots:
                snapshots = _scan_all(cfg.repo_paths)
                last_scan = now
                last_refresh = datetime.now(timezone.utc)

            for ev in tailer.poll():
                feed.appendleft(ev)

            claude = agent_state.read_claude(cfg.claude_state_file)
            codex = agent_state.codex_active(cfg.repo_paths)

            layout["grid"].update(_repo_grid(snapshots))
            layout["agents"].update(_agent_panel(claude, codex))
            layout["feed"].update(_feed_panel(feed))
            layout["bottom"].update(_command_panel(last_result, last_refresh))

            key = _read_key_nonblocking()
            if key in ("q", "Q"):
                break
            elif key in ("r", "R"):
                last_scan = 0.0
                last_result = "refresh queued"
            elif key in ("p", "P"):
                live.stop()
                repo = _pick_repo(console, cfg)
                if repo:
                    res = commands.git_push(repo)
                    last_result = f"push {repo.name}: {res.message[:80]}"
                live.start()
            elif key in ("e", "E"):
                live.stop()
                repo = _pick_repo(console, cfg)
                if repo:
                    res = commands.open_claude_md(repo, editor=cfg.editor)
                    last_result = f"edit {repo.name}: {res.message[:80]}"
                live.start()
            elif key in ("t", "T"):
                live.stop()
                repo = _pick_repo(console, cfg)
                if repo:
                    task_id = _prompt(console, "task_id:")
                    body = _prompt(console, "objective:")
                    if task_id and body:
                        packet = (
                            f"# Task Packet: {task_id}\n"
                            f"**Created:** {datetime.now(timezone.utc).date().isoformat()}\n\n"
                            "## Objective\n\n" + body + "\n"
                        )
                        res = commands.drop_packet(repo, task_id, packet)
                        last_result = f"drop {repo.name}/{task_id}: {res.message[:80]}"
                live.start()

            time.sleep(0.25)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
```

- [ ] **Step 7.3: Verify**

```powershell
python -m pytest tests/test_legion_nerve_center_smoke.py -v
python -m py_compile legion/nerve_center.py legion/config.py legion/repo_scan.py legion/ndjson_tail.py legion/agent_state.py legion/commands.py
```
Expected: smoke test passes; py_compile silent.

- [ ] **Step 7.4: Manual smoke**

```powershell
pip install rich
python -m legion.nerve_center
```
Visual checks: repo grid populated, `project-nexus` shows `N`, activity feed updates as monitor writes, `q` exits cleanly.

- [ ] **Step 7.5: Commit**

```bash
git add legion/nerve_center.py tests/test_legion_nerve_center_smoke.py
git commit -m "legion: nerve_center TUI entry point (Rich Live + 4 panels)"
```

---

### Task 8: Wire up and update quartet files

**Files:**
- Create: `legion/__main__.py`
- Modify: `CHANGELOG.md`
- Modify: `TODO.md`

- [ ] **Step 8.1: Create `legion/__main__.py`**

```python
from legion.nerve_center import main

raise SystemExit(main())
```

- [ ] **Step 8.2: Update `CHANGELOG.md`** — prepend:

```markdown
## 2026-05-05 — Legion Nerve Center v1

- Added `legion/` package: cross-repo live TUI dashboard.
- Panels: Repo Grid (all repos, git state + Nexus harness), Activity Feed (NDJSON tail), Agent Status (Claude ctx + Codex tasks), Command Bar.
- Read-only filesystem watcher, no network in v1.
- Entry: `python -m legion` (config at `legion/config.json`).
```

- [ ] **Step 8.3: Update `TODO.md`** — add under Done:

```markdown
- [x] Phase 7 — Legion Nerve Center v1 (read-only TUI: repo grid + feed + agent status + command bar)
```

- [ ] **Step 8.4: Final verification**

```powershell
python -m pytest tests/test_legion_config.py tests/test_legion_repo_scan.py tests/test_legion_ndjson_tail.py tests/test_legion_agent_state.py tests/test_legion_commands.py tests/test_legion_nerve_center_smoke.py -v
python -m legion --help
```
Expected: all tests pass; `--help` prints usage.

- [ ] **Step 8.5: Commit**

```bash
git add legion/__main__.py CHANGELOG.md TODO.md
git commit -m "legion: __main__, update CHANGELOG and TODO"
```

---

## Risk register

| Risk | Mitigation |
|---|---|
| `git status` on 30+ repos blocks UI | ThreadPoolExecutor(max_workers=8), 5s timeout per repo |
| Huge ndjson files | Tailer only reads appended chunk; never re-reads existing bytes |
| File locks on Windows during monitor write | Tailer opens read-only `open("rb")` |
| `code` not on PATH | `open_claude_md` returns `ok=False` with error; user edits `editor` in config.json |
| Missing/moved repo | `scan_repo` always returns snapshot with `error` populated; renders in red, no crash |
| `msvcrt` not on POSIX | Key reader returns `None`; dashboard still renders; v1 is Windows-first |

## Out of scope (v2+)

- Sending commands directly to Claude/Codex terminals (requires named pipes)
- API usage tracking (requires key handling)
- Auto-writing the Claude state file (a hook can do this — out of scope here)
- Cross-machine sync
