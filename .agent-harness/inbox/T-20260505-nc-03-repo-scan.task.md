# Task Packet: T-20260505-nc-03-repo-scan

**Type:** code_implementation
**Sprint:** Legion Nerve Center v1
**Sequence:** 3 of 8
**Plan:** docs/plans/2026-05-05-legion-nerve-center.md — Task 3

## Objective

Implement the repo scanner (`legion/repo_scan.py`) — a pure function that probes any repo for git state (branch, dirty, ahead/behind, last commit age) and Nexus harness state (active task, phase status). Never raises — errors land in `snapshot.error`.

## Scope

Implement exactly Task 3 from the plan.

- Create `tests/test_legion_repo_scan.py` (7 tests)
- Create `legion/repo_scan.py` with `RepoSnapshot` dataclass and `scan_repo(path)` function

## Branch

Work on branch: `task/T-20260505-nc-03-repo-scan`
Branch from: `task/T-20260505-nc-02-config`

## Acceptance Criteria

- [ ] `python -m pytest tests/test_legion_repo_scan.py -v` → 7 passed
- [ ] `scan_repo` never raises — missing dirs, non-git dirs, git timeouts all return `RepoSnapshot` with `error` populated
- [ ] All changes committed

## Verification Commands

```
python -m pytest tests/test_legion_repo_scan.py -v
```

## Next Task

T-20260505-nc-04-ndjson-tail
