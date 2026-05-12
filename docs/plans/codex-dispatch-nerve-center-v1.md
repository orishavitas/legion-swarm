# Codex Dispatch — Legion Nerve Center v1

**Date:** 2026-05-12
**Repo:** `C:/Users/OriShavit/Documents/GitHub/legion-swarm`
**Sprint:** Sprint 08
**Skill:** nexus-task
**Sequencing:** Tasks are strictly sequential. Do NOT start the next task until the previous task's result file is countersigned by the monitor (a `.countersigned.md` file appears in `.agent-harness/reviews/`).

---

## Context

The `legion/` Python package does not exist yet. All 8 task packets are written and waiting in `.agent-harness/inbox/`. The implementation plan is at `docs/plans/2026-05-05-legion-nerve-center.md` — read it for full file contents, test code, and acceptance criteria before starting each task.

The monitor is NOT running in this repo (it lives in `project_nexus/project-nexus`). After completing each task, write your result file to `.agent-harness/outbox/` using the nexus-task result format. Claude will countersign manually.

---

## Task 1 — T-20260505-nc-01-scaffold

**Packet:** `.agent-harness/inbox/T-20260505-nc-01-scaffold.task.md`
**Branch:** `task/T-20260505-nc-01-scaffold`

**Files to create:**
- `legion/__init__.py` — `__version__ = "0.1.0"` with module docstring
- `legion/requirements.txt` — `rich>=13.7` and `pytest>=8.0`
- `legion/README.md` — how to run (`python -m legion`) and edit `legion/config.json`
- Append `legion/state/` to `.gitignore`

**Acceptance criteria:**
- `python -c "import legion; print(legion.__version__)"` prints `0.1.0`
- `legion/requirements.txt` contains `rich>=13.7` and `pytest>=8.0`
- `legion/state/` is in `.gitignore`
- All changes committed on branch `task/T-20260505-nc-01-scaffold`

**Verify:** `python -c "import legion; print(legion.__version__)"`
**Commit message:** `legion: scaffold package and requirements`

---

## Task 2 — T-20260505-nc-02-config

**Packet:** `.agent-harness/inbox/T-20260505-nc-02-config.task.md`
**Branch:** `task/T-20260505-nc-02-config`
**Dependency:** Task 1 countersigned

**Files to create:**
- `legion/config.py` — `load_config(path)` returning a `Config` dataclass; `repos: []` triggers auto-discovery of all `.git/` dirs under `repos_root`
- `tests/test_legion_config.py` — 5 tests (see plan Task 2 for full test code)
- `legion/config.json` — `{"repos_root": "C:/Users/OriShavit/Documents/GitHub", "repos": [], "refresh_seconds": 30, "feed_max_lines": 200, "claude_state_file": "...", "editor": "code"}`

**Acceptance criteria:**
- `python -m pytest tests/test_legion_config.py -v` reports 5 passed
- `legion/config.json` exists with `repos_root` set
- `repos: []` auto-discovers all `.git/` dirs under `repos_root`
- All changes committed

---

## Task 3 — T-20260505-nc-03-repo-scan

**Packet:** `.agent-harness/inbox/T-20260505-nc-03-repo-scan.task.md`
**Branch:** `task/T-20260505-nc-03-repo-scan`
**Dependency:** Task 2 countersigned

**Files to create:**
- `legion/repo_scan.py` — `scan_repo(path) -> RepoSnapshot`; fields: `name`, `branch`, `dirty`, `ahead`, `behind`, `is_nexus`, `active_task`, `last_event`
- `tests/test_legion_repo_scan.py` — tests: basic scan, dirty detection, nexus detection, active task read (see plan Task 3)

**Acceptance criteria:**
- `python -m pytest tests/test_legion_repo_scan.py -v` reports 4+ passed
- `scan_repo` never raises on a valid git repo; returns defaults on errors
- All changes committed

---

## Task 4 — T-20260505-nc-04-ndjson-tail

**Packet:** `.agent-harness/inbox/T-20260505-nc-04-ndjson-tail.task.md`
**Branch:** `task/T-20260505-nc-04-ndjson-tail`
**Dependency:** Task 3 countersigned

**Files to create:**
- `legion/ndjson_tail.py` — `MultiTailer(sources: dict[str, Path])`; `poll() -> list[dict]` returns only new lines since last poll; injects `repo` key from source name; skips malformed JSON lines
- `tests/test_legion_ndjson_tail.py` — 4 tests (see plan Task 4)

**Acceptance criteria:**
- `python -m pytest tests/test_legion_ndjson_tail.py -v` reports 4 passed
- `poll()` is idempotent — second call on unchanged file returns `[]`
- All changes committed

---

## Task 5 — T-20260505-nc-05-agent-state

**Packet:** `.agent-harness/inbox/T-20260505-nc-05-agent-state.task.md`
**Branch:** `task/T-20260505-nc-05-agent-state`
**Dependency:** Task 4 countersigned

**Files to create:**
- `legion/agent_state.py` — `read_claude(path) -> ClaudeState`; fields: `present`, `context_pct_used`, `model`, `current_repo`, `stale`; stale threshold = 5 minutes
- `tests/test_legion_agent_state.py` — 3 tests: missing file, fresh state, stale state (see plan Task 5)

**Acceptance criteria:**
- `python -m pytest tests/test_legion_agent_state.py -v` reports 3 passed
- Missing/unreadable file returns `ClaudeState(present=False)` without raising
- All changes committed

---

## Task 6 — T-20260505-nc-06-commands

**Packet:** `.agent-harness/inbox/T-20260505-nc-06-commands.task.md`
**Branch:** `task/T-20260505-nc-06-commands`
**Dependency:** Task 5 countersigned

**Files to create:**
- `legion/commands.py` — `drop_packet(repo_path, task_id, content) -> CommandResult`; validates task_id (no spaces, no slashes); writes to `.agent-harness/inbox/{task_id}.task.md`; returns `CommandResult(ok, message)`
- `tests/test_legion_commands.py` — 3 tests: happy path, bad id, missing inbox dir (see plan Task 6)

**Acceptance criteria:**
- `python -m pytest tests/test_legion_commands.py -v` reports 3 passed
- All changes committed

---

## Task 7 — T-20260505-nc-07-tui

**Packet:** `.agent-harness/inbox/T-20260505-nc-07-tui.task.md`
**Branch:** `task/T-20260505-nc-07-tui`
**Dependency:** Task 6 countersigned

**Files to create:**
- `legion/nerve_center.py` — Rich Live TUI; `build_layout() -> Layout`; `main(argv=None) -> int`; four panels: Repo Grid, Activity Feed, Agent Status, Command Bar; reads from `config.py`, `repo_scan.py`, `ndjson_tail.py`, `agent_state.py`; `--once` flag renders one frame and exits (for testing)
- `tests/test_legion_nerve_center_smoke.py` — 2 tests: module imports, `build_layout` returns a Layout (see plan Task 7)

**Acceptance criteria:**
- `python -m pytest tests/test_legion_nerve_center_smoke.py -v` reports 2 passed
- `python -m legion --once` exits 0 without raising (requires `legion/config.json` present)
- All changes committed

---

## Task 8 — T-20260505-nc-08-wire-up

**Packet:** `.agent-harness/inbox/T-20260505-nc-08-wire-up.task.md`
**Branch:** `task/T-20260505-nc-08-wire-up`
**Dependency:** Task 7 countersigned

**Files to create/modify:**
- `legion/__main__.py` — `from legion.nerve_center import main; raise SystemExit(main())`
- Prepend to `CHANGELOG.md`: `## 2026-05-05 — Legion Nerve Center v1` entry (see plan Task 8)
- Update `TODO.md`: mark `Phase 7 — Legion Nerve Center v1` done

**Acceptance criteria:**
- `python -m pytest tests/test_legion_config.py tests/test_legion_repo_scan.py tests/test_legion_ndjson_tail.py tests/test_legion_agent_state.py tests/test_legion_commands.py tests/test_legion_nerve_center_smoke.py -v` — all pass
- `python -m legion --help` prints usage without error
- All changes committed on branch `task/T-20260505-nc-08-wire-up`

---

## Result Format (each task)

Write result to `.agent-harness/outbox/T-20260505-nc-0N-[slug].result.md`:

```markdown
# Result: T-20260505-nc-0N-[slug]
task_id: T-20260505-nc-0N-[slug]
completed_at: [ISO timestamp]
NEXUS_VERIFICATION: PASSED

## Summary
[what was done]

## Acceptance Criteria
- [x] criterion 1
- [x] criterion 2

## Verification Commands Run
[commands + outputs]

## Files Changed
[list]
```
