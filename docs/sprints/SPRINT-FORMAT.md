# Sprint File Format Reference

Sprint files are the shared sync point between Claude/Legion (writes tasks, reads completions) and Codex (reads tasks, writes progress + blocks).

## File Naming
```
YYYY-MM-DD-[repo]-sprint-NN-[slug].md
```

## File Header
```markdown
# Sprint NN — [Title]
> [Repo] | [Date] | Status: Ready | in_progress | blocked | done

## Goal
[One paragraph. What does this sprint deliver and why.]
```

## Task Block Format

Each task uses this exact structure. Codex reads and writes the Status and Blocked reason fields.

```markdown
### Task N: [Title]

[Description of what to build.]

**Acceptance Criteria:**
- [ ] [Verifiable outcome]
- [ ] [Verifiable outcome]

**Verify:** [How to confirm this task is done.]

**Commit:** `[conventional commit message]`

**Status:** pending
**Blocked reason:**
```

### Status Values

| Value | Set by | Meaning |
|-------|--------|---------|
| `pending` | Legion/Claude | Not started |
| `in_progress` | Codex | Codex is working on it |
| `blocked` | Codex | Codex cannot proceed — see blocked_reason |
| `done` | Codex | AC verified, tests pass |

### Blocked Reason
- Written by Codex when it cannot proceed
- Format: `"Claude needs to: [specific action]"`
- Legion reads this, resolves it, then resets status to `pending` for Codex to retry

## Done Criteria Block (end of file)

```markdown
## Done Criteria

- [ ] [Sprint-level outcome 1]
- [ ] [Sprint-level outcome 2]

## Out of Scope

- [Explicitly excluded items]
```
