# Claude ↔ Codex Dialogue Format

> Shared communication protocol between Claude (orchestrator/reviewer) and Codex (builder/code reviewer).
> All messages are appended to `.codex/state/DIALOGUE.md` in the repo being worked on.
> `.codex/state/TURN.md` controls who acts next.

## File Locations (per repo)

```
[repo-root]/
  .codex/
    state/
      DIALOGUE.md    ← append-only message log
      TURN.md        ← "claude" or "codex" — who acts next
```

## Message Format

Every message appended to `DIALOGUE.md` uses this exact block:

```
---
from: claude | codex
type: task | review | question | decision | result | blocker | test-request | test-result
ref: [task_id, file path, or "general"]
timestamp: [ISO8601]
monday_item_id: [optional — Monday board item ID to log this against]
---
[message content]

[DIALOGUE_END]
```

## Message Types

| Type | Written by | Meaning |
|------|-----------|---------|
| `task` | Claude | Assign a build task to Codex |
| `review` | Claude | Claude's review of Codex output |
| `question` | Either | Needs answer before proceeding |
| `decision` | Claude | Architectural/product decision, Codex must not reverse |
| `result` | Codex | Build/review complete, here's the output |
| `blocker` | Codex | Cannot proceed, Claude must resolve |
| `test-request` | Claude | Claude asking Codex to run specific tests |
| `test-result` | Codex | Test output back to Claude |

## TURN.md Protocol

- Contains exactly one word: `claude` or `codex`
- Writer sets TURN to the other party after appending their message
- Codex checks TURN.md at session start — if `claude`, it waits (reads only, no write)
- Claude checks TURN.md before dispatching — if `codex`, Codex is mid-task

## Monday Logging

Every message with a `monday_item_id` gets logged by Claude to the Monday board item as an update.

Log format written to Monday:
```
[DIALOGUE] from=[claude|codex] type=[type] ref=[ref]
[first 200 chars of message content]
→ Turn: [claude|codex]
```

Claude runs this log after every message exchange. Codex does not write to Monday directly — Claude reads Codex's `DIALOGUE.md` entries and logs them on Codex's behalf.

## Example Exchange

```
---
from: claude
type: task
ref: task-003
timestamp: 2026-05-03T09:00:00Z
monday_item_id: 11890230867
---
Implement the `parseDialogue()` function in `src/dialogue/parser.ts`.
AC:
- Parses all 8 message types correctly
- Returns structured DialogueMessage[]
- 100% test coverage on type parsing

[DIALOGUE_END]

---
from: codex
type: result
ref: task-003
timestamp: 2026-05-03T09:45:00Z
monday_item_id: 11890230867
---
Done. `parseDialogue()` implemented and tested.
Files: src/dialogue/parser.ts, src/dialogue/parser.test.ts
Tests: 24 passed, 0 failed
Coverage: 100% on parser.ts
Remaining risk: none

[DIALOGUE_END]

---
from: claude
type: review
ref: task-003
timestamp: 2026-05-03T10:00:00Z
monday_item_id: 11890230867
---
Review PASS.
- Logic correct, types clean
- One note: add JSDoc to parseDialogue() signature for future agents
- Performance: 24 tests in <1s — acceptable
Next: task-004

[DIALOGUE_END]
```

## Stop Conditions

Codex stops responding to dialogue when:
- `TURN.md` says `claude` — Claude must act first
- Message type is `decision` — Codex reads it, does not respond unless asked
- Message type is `question` directed at Claude — Codex waits

Claude stops dispatching when:
- `TURN.md` says `codex` — Codex is still working
- Last Codex message is type `blocker` — must resolve before continuing
