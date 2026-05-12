# Task Packet: T-20260505-nc-05-agent-state

**Type:** code_implementation
**Sprint:** Legion Nerve Center v1
**Sequence:** 5 of 8
**Plan:** docs/plans/2026-05-05-legion-nerve-center.md — Task 5

## Objective

Implement the agent state reader (`legion/agent_state.py`). Reads Claude's state file (`legion/state/claude.json`) and scans Codex inbox packets across all repos. Handles missing files, stale state (>5 min old), and malformed JSON gracefully.

## Scope

Implement exactly Task 5 from the plan.

- Create `tests/test_legion_agent_state.py` (4 tests)
- Create `legion/agent_state.py` with `ClaudeState` dataclass, `read_claude(path)`, and `codex_active(repo_paths)`

## Branch

Work on branch: `task/T-20260505-nc-05-agent-state`
Branch from: `task/T-20260505-nc-04-ndjson-tail`

## Acceptance Criteria

- [ ] `python -m pytest tests/test_legion_agent_state.py -v` → 4 passed
- [ ] Missing state file returns `ClaudeState(present=False)` — no exception
- [ ] State older than 5 minutes has `stale=True`
- [ ] All changes committed

## Verification Commands

```
python -m pytest tests/test_legion_agent_state.py -v
```

## Next Task

T-20260505-nc-06-commands
