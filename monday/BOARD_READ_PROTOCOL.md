# Legion Board Read Protocol

How Legion reads the Monday board to derive sprint state. Follow this call sequence exactly.

---

## Session Open Read

Called at every Legion session start, after loading quartet files.

**Step 1 — Get board:**
```
mcp__claude_ai_monday_com__get_board_info({ board_name: "[{repo-name}] — Legion Swarm" })
```
Extract `board_id`.

**Step 2 — Get active items:**
```
mcp__claude_ai_monday_com__get_board_items_page({
  board_id: <board_id>,
  group_id: "sprint_active"
})
```

**Step 3 — Read columns for each item:**
For each item: read `Agent`, `Status`, `Current Task`, `Last Update`, `Ping Required`, `Map Update Required`.

**Step 4 — Build standup summary:**
```
[N] agents active | [N] blocked | [N] need pings
```
Surface this to Shepard-Commander at session open.

---

## Ping Sweep

After the session open read, check every item in `Sprint Active` for `Ping Required = true`.

For each flagged item:
1. Read `Last Update` — extract the blocked reason or decision needed
2. Send Google Chat ping via `ping_shepherd`:
   - `agent`: the item's `Agent` value
   - `status`: `BLOCKED` or `NEEDS_DECISION` (from Status column)
   - `message`: the Last Update text
   - `repo`: current repo name
   - `monday_url`: direct link to the board item
3. Clear the flag: `change_item_column_values({ ping_required: { checked: false } })`

Do not clear the flag before sending the ping.

---

## Sprint Completion Detection

Sprint is complete when **all items** in `Sprint Active` group have `Status = Done`.

When detected:
1. Send ping via `ping_shepherd`: `status=DONE`, `message="Sprint complete. All [N] tasks done. Awaiting authorization to archive."`
2. Wait for Shepard-Commander authorization before moving items to `Done` group
3. Do not auto-archive — explicit authorization required
