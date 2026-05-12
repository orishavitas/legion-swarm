# Task Packet: T-20260505-nc-06-commands

**Type:** code_implementation
**Sprint:** Legion Nerve Center v1
**Sequence:** 6 of 8
**Plan:** docs/plans/2026-05-05-legion-nerve-center.md — Task 6

## Objective

Implement the v1 command actions (`legion/commands.py`): drop a task packet into a repo's inbox, run git push, open a repo's CLAUDE.md in editor. All actions return `CommandResult(ok, message)` — never raise.

## Scope

Implement exactly Task 6 from the plan.

- Create `tests/test_legion_commands.py` (6 tests)
- Create `legion/commands.py` with `CommandResult`, `drop_packet()`, `open_claude_md()`, `git_push()`

## Branch

Work on branch: `task/T-20260505-nc-06-commands`
Branch from: `task/T-20260505-nc-05-agent-state`

## Acceptance Criteria

- [ ] `python -m pytest tests/test_legion_commands.py -v` → 6 passed
- [ ] `drop_packet` rejects task IDs with spaces or special chars
- [ ] `drop_packet` refuses to overwrite an existing packet
- [ ] `git_push` on a repo with no remote returns `ok=False` (not an exception)
- [ ] All changes committed

## Verification Commands

```
python -m pytest tests/test_legion_commands.py -v
```

## Next Task

T-20260505-nc-07-tui
