# [Repo Name] — Codex KB

> Codex reads this file once at session start. It is the single source of truth for repo-specific context.
> Update this file whenever conventions, stack, or known issues change.
> For cross-repo and product-level context, see the Obsidian wiki (path below).

## What This Repo Does
[1-2 sentences. What product does this repo implement? Who uses it?]

## Obsidian Wiki
- **Project page:** `~/obsidian/legion-wiki/wiki/projects/[repo-slug].md`
- **Key concepts:** [link to relevant wiki concept pages if any]
- Read the project page for architecture decisions, product context, and cross-repo dependencies that are too broad for this file.

## Stack
- Language / runtime:
- Framework:
- Test runner:
- Package manager:
- Key dependencies:

## Repo Layout
```
[paste key dirs/files and what they do]
```

## Conventions
- [naming conventions, code style, branching rules]
- [how tests are structured and run]
- [anything a new dev would get wrong on day 1]

## Known Issues / Gotchas
- [list anything Codex should not break or should be aware of]

## Key Files to Know
| File | Purpose |
|------|---------|
| [path] | [why it matters] |

## How to Run Tests
```bash
[exact command]
```

## How to Run the App Locally
```bash
[exact command, if applicable]
```

## Codex Runtime State
> `.codex/state/` in repo root — Codex reads and writes these every session.

| File | Written by | Purpose |
|------|-----------|---------|
| `TASK_STATE.md` | Legion | Current objective, constraints, task context |
| `LAST_RUN.md` | Codex | What last session did, commands run, result, remaining risk |
| `DECISIONS.md` | Legion / Codex | Architectural/product decisions that must not be reversed |
| `HANDOFF_[ts].md` | `codex-handoff.ps1` | Timestamped snapshot of state + git at session end |

Scripts:
- `scripts/codex-handoff.ps1` — run at session end (done or blocked) to write `HANDOFF_[timestamp].md`

Stop conditions (Codex must stop and write BLOCKED):
- Tests fail twice for the same unclear reason
- Unrelated dirty files in git status
- Next step requires product or architecture judgment
- `git push --dry-run` fails (remote auth broken)
