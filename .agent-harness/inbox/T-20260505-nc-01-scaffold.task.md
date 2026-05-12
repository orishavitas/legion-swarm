# Task Packet: T-20260505-nc-01-scaffold

**Type:** code_implementation
**Sprint:** Legion Nerve Center v1
**Sequence:** 1 of 8
**Plan:** docs/plans/2026-05-05-legion-nerve-center.md — Task 1

## Objective

Scaffold the `legion/` Python package in this repo (`legion-swarm`). Create the package init, requirements file, README, and add `legion/state/` to `.gitignore`.

## Scope

Implement exactly Task 1 from the plan. Nothing more.

- Create `legion/__init__.py`
- Create `legion/requirements.txt`
- Create `legion/README.md`
- Append `legion/state/` to `.gitignore`

## Branch

Work on branch: `task/T-20260505-nc-01-scaffold`

## Acceptance Criteria

- [ ] `python -c "import legion; print(legion.__version__)"` prints `0.1.0`
- [ ] `legion/requirements.txt` contains `rich>=13.7` and `pytest>=8.0`
- [ ] `legion/state/` is in `.gitignore`
- [ ] All changes committed on branch `task/T-20260505-nc-01-scaffold`

## Verification Commands

```
python -c "import legion; print(legion.__version__)"
```

## Next Task

T-20260505-nc-02-config (do not start until this task's result is countersigned)
