# Task Packet: T-20260505-nc-04-ndjson-tail

**Type:** code_implementation
**Sprint:** Legion Nerve Center v1
**Sequence:** 4 of 8
**Plan:** docs/plans/2026-05-05-legion-nerve-center.md — Task 4

## Objective

Implement the multi-file NDJSON tailer (`legion/ndjson_tail.py`). Stateful polling — keeps byte offsets per file, returns only new events on each `poll()`, handles truncation, missing files, and malformed lines without raising.

## Scope

Implement exactly Task 4 from the plan.

- Create `tests/test_legion_ndjson_tail.py` (5 tests)
- Create `legion/ndjson_tail.py` with `MultiTailer` class

## Branch

Work on branch: `task/T-20260505-nc-04-ndjson-tail`
Branch from: `task/T-20260505-nc-03-repo-scan`

## Acceptance Criteria

- [ ] `python -m pytest tests/test_legion_ndjson_tail.py -v` → 5 passed
- [ ] Truncation test passes (file shrinks → offset resets → re-reads from 0)
- [ ] Malformed JSON lines are silently skipped
- [ ] All changes committed

## Verification Commands

```
python -m pytest tests/test_legion_ndjson_tail.py -v
```

## Next Task

T-20260505-nc-05-agent-state
