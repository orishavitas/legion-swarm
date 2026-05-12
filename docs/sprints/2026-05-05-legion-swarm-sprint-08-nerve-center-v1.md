# Sprint 08 - Legion Nerve Center v1
> Legion Swarm | 2026-05-05 | Status: Ready

## Goal

Build the Legion Nerve Center v1: a read-only Rich Live TUI dashboard that gives the operator one local view over repos under `C:/Users/OriShavit/Documents/GitHub/`, including repo git state, Nexus harness activity, Claude/Codex state, and local command actions. The detailed implementation source of truth is `docs/plans/2026-05-05-legion-nerve-center.md`.

## Sequencing Rule

- Execute tasks strictly in numeric order.
- Dispatch only one Codex task at a time.
- Do not start the next task until the previous task's outbox result and artifact evidence are monitor-countersigned.
- Downstream tasks remain `blocked` until their dependency is countersigned, then Legion resets the next task to `pending`.

---

## Tasks

### Task 1: T-20260505-nc-01-scaffold - Scaffold `legion/` package and requirements

Implement exactly Task 1 from `docs/plans/2026-05-05-legion-nerve-center.md`.

Files:
- Create `legion/__init__.py`
- Create `legion/requirements.txt`
- Create `legion/README.md`
- Append `legion/state/` to `.gitignore`

Task packet: `.agent-harness/inbox/T-20260505-nc-01-scaffold.task.md`
Branch: `task/T-20260505-nc-01-scaffold`

**Acceptance Criteria:**
- [ ] `python -c "import legion; print(legion.__version__)"` prints `0.1.0`
- [ ] `legion/requirements.txt` contains `rich>=13.7` and `pytest>=8.0`
- [ ] `legion/state/` is in `.gitignore`
- [ ] All changes are committed on branch `task/T-20260505-nc-01-scaffold`

**Verify:** `python -c "import legion; print(legion.__version__)"`

**Commit:** `legion: scaffold package and requirements`

**Status:** done
**Blocked reason:**

---

### Task 2: T-20260505-nc-02-config - Config loader

Implement exactly Task 2 from `docs/plans/2026-05-05-legion-nerve-center.md`.

Task packet: `.agent-harness/inbox/T-20260505-nc-02-config.task.md`
Branch: `task/T-20260505-nc-02-config`
Dependency: Task 1 monitor countersignature.

**Acceptance Criteria:**
- [ ] `python -m pytest tests/test_legion_config.py -v` reports 5 passed
- [ ] `legion/config.json` exists with `repos_root` set to `C:/Users/OriShavit/Documents/GitHub`
- [ ] `repos: []` auto-discovers all `.git/` dirs under `repos_root`
- [ ] All changes are committed

**Verify:** `python -m pytest tests/test_legion_config.py -v`

**Commit:** `legion: config loader with validation and autodiscovery`

**Status:** done
**Blocked reason:**

---

### Task 3: T-20260505-nc-03-repo-scan - Repo scanner

Implement exactly Task 3 from `docs/plans/2026-05-05-legion-nerve-center.md`.

Task packet: `.agent-harness/inbox/T-20260505-nc-03-repo-scan.task.md`
Branch: `task/T-20260505-nc-03-repo-scan`
Dependency: Task 2 monitor countersignature.

**Acceptance Criteria:**
- [ ] `python -m pytest tests/test_legion_repo_scan.py -v` reports 7 passed
- [ ] `scan_repo` never raises for missing dirs, non-git dirs, or git timeouts
- [ ] Errors are returned in `RepoSnapshot.error`
- [ ] All changes are committed

**Verify:** `python -m pytest tests/test_legion_repo_scan.py -v`

**Commit:** `legion: repo_scan probe for git + harness state`

**Status:** done
**Blocked reason:**

---

### Task 4: T-20260505-nc-04-ndjson-tail - Multi-file NDJSON tailer

Implement exactly Task 4 from `docs/plans/2026-05-05-legion-nerve-center.md`.

Task packet: `.agent-harness/inbox/T-20260505-nc-04-ndjson-tail.task.md`
Branch: `task/T-20260505-nc-04-ndjson-tail`
Dependency: Task 3 monitor countersignature.

**Acceptance Criteria:**
- [ ] `python -m pytest tests/test_legion_ndjson_tail.py -v` reports 5 passed
- [ ] Truncation resets offsets correctly
- [ ] Malformed JSON lines are skipped without raising
- [ ] All changes are committed

**Verify:** `python -m pytest tests/test_legion_ndjson_tail.py -v`

**Commit:** `legion: multi-file NDJSON tailer`

**Status:** done
**Blocked reason:**

---

### Task 5: T-20260505-nc-05-agent-state - Agent state reader

Implement exactly Task 5 from `docs/plans/2026-05-05-legion-nerve-center.md`.

Task packet: `.agent-harness/inbox/T-20260505-nc-05-agent-state.task.md`
Branch: `task/T-20260505-nc-05-agent-state`
Dependency: Task 4 monitor countersignature.

**Acceptance Criteria:**
- [ ] `python -m pytest tests/test_legion_agent_state.py -v` reports 4 passed
- [ ] Missing Claude state file returns `ClaudeState(present=False)`
- [ ] State older than 5 minutes has `stale=True`
- [ ] All changes are committed

**Verify:** `python -m pytest tests/test_legion_agent_state.py -v`

**Commit:** `legion: agent_state reader for Claude + Codex`

**Status:** done
**Blocked reason:**

---

### Task 6: T-20260505-nc-06-commands - Command actions

Implement exactly Task 6 from `docs/plans/2026-05-05-legion-nerve-center.md`.

Task packet: `.agent-harness/inbox/T-20260505-nc-06-commands.task.md`
Branch: `task/T-20260505-nc-06-commands`
Dependency: Task 5 monitor countersignature.

**Acceptance Criteria:**
- [ ] `python -m pytest tests/test_legion_commands.py -v` reports 6 passed
- [ ] `drop_packet` rejects invalid task IDs
- [ ] `drop_packet` refuses to overwrite existing packets
- [ ] `git_push` returns `ok=False` on a repo with no remote
- [ ] All changes are committed

**Verify:** `python -m pytest tests/test_legion_commands.py -v`

**Commit:** `legion: command actions (drop_packet, git_push, open_claude_md)`

**Status:** done
**Blocked reason:**

---

### Task 7: T-20260505-nc-07-tui - Rich Live TUI entry point

Implement exactly Task 7 from `docs/plans/2026-05-05-legion-nerve-center.md`.

Task packet: `.agent-harness/inbox/T-20260505-nc-07-tui.task.md`
Branch: `task/T-20260505-nc-07-tui`
Dependency: Task 6 monitor countersignature.

**Acceptance Criteria:**
- [ ] `python -m pytest tests/test_legion_nerve_center_smoke.py -v` reports 1 passed
- [ ] `python -m py_compile legion/nerve_center.py` exits 0
- [ ] `python -m legion.nerve_center --help` prints usage without error
- [ ] Manual smoke confirms repo grid renders and `q` exits cleanly
- [ ] All changes are committed

**Verify:** `python -m pytest tests/test_legion_nerve_center_smoke.py -v`; `python -m py_compile legion/nerve_center.py`; `python -m legion.nerve_center --help`

**Commit:** `legion: nerve_center TUI entry point (Rich Live + 4 panels)`

**Status:** done
**Blocked reason:**

---

### Task 8: T-20260505-nc-08-wire-up - Wire up runnable module and quartet files

Implement exactly Task 8 from `docs/plans/2026-05-05-legion-nerve-center.md`.

Task packet: `.agent-harness/inbox/T-20260505-nc-08-wire-up.task.md`
Branch: `task/T-20260505-nc-08-wire-up`
Dependency: Task 7 monitor countersignature.

**Acceptance Criteria:**
- [ ] `python -m legion --help` works
- [ ] Full Nerve Center test suite reports 24 passed
- [ ] `CHANGELOG.md` is updated
- [ ] `TODO.md` is updated
- [ ] All changes are committed

**Verify:** `python -m pytest tests/test_legion_config.py tests/test_legion_repo_scan.py tests/test_legion_ndjson_tail.py tests/test_legion_agent_state.py tests/test_legion_commands.py tests/test_legion_nerve_center_smoke.py -v`; `python -m legion --help`

**Commit:** `legion: __main__, update CHANGELOG and TODO`

**Status:** done
**Blocked reason:**

---

## Done Criteria

- [ ] All 8 Nerve Center task packets are completed in order and countersigned.
- [ ] `python -m legion --help` exits 0 and prints usage.
- [ ] The full Nerve Center test suite reports 24 passed.
- [ ] Monday item state reflects completion or a documented blocker for every task.

## Out of Scope

- API-backed dashboard data in v1.
- Sending commands directly to Claude/Codex terminals.
- API usage tracking or key management.
- Auto-writing Claude state files.
- Cross-machine sync.
