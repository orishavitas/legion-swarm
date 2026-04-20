# Sprint 06 — Google Chat Integration

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans

**Goal:** Build the `google-chat` MCP server so agents and Legion can ping Shepard-Commander asynchronously via Google Chat Incoming Webhook. No OAuth — outbound only.

**Spec:** `docs/specs/2026-04-05-legion-swarm-design.md` Section 6

---

### Task 1: Scaffold the MCP server

- Create `legion-swarm/mcp/google-chat/` with `package.json`, `tsconfig.json`, `src/index.ts`
- Server is a standard MCP server (stdio transport) built with `@modelcontextprotocol/sdk`
- Add `dist/` to `.gitignore`; webhook URL loaded from `process.env.GOOGLE_CHAT_WEBHOOK_URL`
- Add `.env.example` with `GOOGLE_CHAT_WEBHOOK_URL=` (empty — placeholder only, never populate)
- Commit: `feat: scaffold google-chat MCP server`
- **Verify:** `package.json` has `name: "legion-swarm-google-chat"`, `src/index.ts` exists, `.env.example` committed

---

### Task 2: Implement `ping_shepherd` tool

- Expose one tool: `ping_shepherd(message, repo, agent, status, monday_url)`
  - `status` is a string enum: `DONE | BLOCKED | NEEDS_DECISION`
  - Tool constructs the standard Legion Swarm message format and POSTs it to the webhook URL via `fetch`
  - Message format (from spec):
    ```
    [Legion Swarm] {repo} — {agent}
    Status: {status}
    {message}
    Monday: {monday_url}
    ```
  - Sends as `{ "text": "..." }` JSON body — Google Chat Incoming Webhook format
  - Returns `{ ok: true }` on success, throws a descriptive error on HTTP failure
- Commit: `feat: implement ping_shepherd tool with webhook POST`
- **Verify:** Tool is registered in the MCP server manifest; happy-path logic is readable without ambiguity

---

### Task 3: Wire webhook env + add server entry point

- Add a `start` script in `package.json`: `node dist/index.js`
- Add a `build` script: `tsc`
- Document in `README.md` (inside `mcp/google-chat/`): how to get a Google Chat Incoming Webhook URL, where to set `GOOGLE_CHAT_WEBHOOK_URL`, and how to register the server in Claude's MCP config
- Commit: `feat: add build/start scripts and setup README`
- **Verify:** `npm run build` produces `dist/index.js`; README covers all three setup steps

---

### Task 4: Register server in `legion-swarm/.mcp.json`

- Add `google-chat` entry to `legion-swarm/.mcp.json` (create file if it doesn't exist)
- Entry uses `command: "node"`, `args: ["mcp/google-chat/dist/index.js"]`, `env: { "GOOGLE_CHAT_WEBHOOK_URL": "" }` — blank env value; real URL is injected by operator at runtime
- Commit: `feat: register google-chat MCP in .mcp.json`
- **Verify:** `.mcp.json` is valid JSON and parses without error

---

### Task 5: Update agent report format trigger logic

- Update `legion-swarm/meta/CLAUDE.md`: add a section under "Pinging Shepard-Commander" that instructs Legion to call `ping_shepherd` whenever an agent report contains `Ping Shepard-Commander: YES`
- Add the same instruction to all 11 agent identity files in `agents/`: under Report Format, clarify that `Ping Shepard-Commander: YES` means the agent calls `ping_shepherd` directly (not Legion) if the tool is in scope, otherwise Legion handles it
- Commit: `docs: wire Ping Shepard-Commander flag to ping_shepherd tool`
- **Verify:** `meta/CLAUDE.md` and all 11 agent files contain the updated instruction

---

### Task 6: Watchdog usage hard-stop hook

- Update `legion-swarm/meta/CLAUDE.md`: at the `≥95% API usage` threshold, Legion calls `ping_shepherd` with `status: NEEDS_DECISION`, `agent: "Legion"`, `message: "Usage at 95%. Hard stop triggered. All agent terminals closed. System resumes at usage reset."`, and the active Monday board URL
- This is a documentation + identity update only — no new code needed beyond Task 2
- Commit: `docs: add usage hard-stop ping instruction to Legion identity`
- **Verify:** The watchdog section in `meta/CLAUDE.md` references `ping_shepherd` explicitly with the correct status and message template

---

### Done Criteria

- `mcp/google-chat/` builds cleanly with `npm run build`
- `.mcp.json` registers the server
- `ping_shepherd` posts correctly formatted messages to a Google Chat Incoming Webhook
- All 11 agent files and `meta/CLAUDE.md` reference the tool in the correct trigger context
- No webhook URL is committed to the repo at any point
