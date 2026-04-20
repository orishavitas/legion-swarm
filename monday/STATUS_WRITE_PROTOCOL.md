# Agent Status Write Protocol

How specialist agents write status to Monday. Follow this exactly — no improvisation.

---

## Columns Agents Write

| Column | When to write |
|--------|--------------|
| `Current Task` | Once, when the task starts |
| `Last Update` | On every status change (Active → Done, Active → Blocked, etc.) |
| `Status` | On every status change — use the dropdown values only |
| `Ping Required` | Set `true` when status is `Blocked` or `Needs Decision` |
| `Map Update Required` | Set `true` when Mapper should re-scan after your work |

## Columns Agents Never Write

| Column | Who sets it |
|--------|------------|
| `Agent` | Launcher MCP at session spawn |
| `Terminal ID` | Launcher MCP at session spawn |
| `Idle` status | Launcher MCP only |

---

## Last Update Format

Single line, max 120 characters:

```
[YYYY-MM-DD HH:MM] [STATUS] [what happened or what is blocked on]
```

**Examples:**
- `2026-04-05 14:32 DONE Refactored auth middleware, reduced 3 functions to 1`
- `2026-04-05 15:01 BLOCKED Cannot proceed — missing API key for external service`
- `2026-04-05 09:45 ACTIVE Starting implementation of login form`

---

## Status State Machine

| Status value | When to set | Additional action |
|-------------|-------------|------------------|
| `Active` | Immediately when task starts | Set `Current Task` |
| `Done` | When work is complete and report is written | Set `Ping Required = false` |
| `Blocked` | Cannot proceed | Set `Ping Required = true` |
| `Needs Decision` | Product or design ambiguity | Set `Ping Required = true` |
| `Idle` | **Never set by agents** | Set by Launcher only |

---

## MCP Call Pattern

For a status change to `Done`:
```
mcp__claude_ai_monday_com__change_item_column_values({
  board_id: <board_id>,
  item_id: <item_id>,
  column_values: {
    status: { label: "Done" },
    last_update: "[2026-04-05 14:32] DONE Task completed successfully",
    ping_required: { checked: false }
  }
})
```
