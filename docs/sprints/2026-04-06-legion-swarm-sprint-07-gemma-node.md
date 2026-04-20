# Sprint 07 — Gemma 4 Local Compute Node
> Legion Swarm | 2026-04-06 | Status: Ready

## Goal

Add a Gemma 4 26B local compute node to Legion Swarm. Agents call it explicitly for mechanical tasks (boilerplate, docstrings, scaffolding, repetitive transforms), reducing Claude API spend. Phase 1: manual routing only — agents decide when to call it. The node is a lightweight MCP server wrapping Ollama's OpenAI-compatible API at `http://localhost:11434`.

---

## Architecture Decisions

### Why an MCP server and not a plain fetch helper?

An MCP server makes `gemma()` a first-class tool any agent can invoke without importing a helper module or knowing the Ollama URL. It also gives the Watchdog a single health-check surface. Cost: one extra process. Acceptable for a persistent local node.

### Why Ollama over Docker?

Simpler lifecycle on Windows — no daemon management, automatic VRAM offload, easy model pinning. Docker is documented as fallback in the research doc.

### Context window caveat

Gemma 4's context window size was not published in release notes as of 2026-04-06. The MCP server will default to passing prompts as-is. If a confirmed window size surfaces, add a truncation guard in a follow-on task.

### Routing is explicit in Phase 1

No automatic classification. Agents read routing guidance from `meta/CLAUDE.md` and call `gemma()` by hand. Phase 2 (automatic dispatcher) is out of scope for this sprint.

---

## Tasks

### Task 0 — Pre-flight: verify Ollama + Gemma 4 availability

**What to build:** Nothing. Run diagnostics only. This gates all subsequent tasks.

**Steps:**
1. Run `ollama list` — check whether `gemma4:26b` appears.
2. Run `ollama show gemma4:26b` — capture context window field if present.
3. Run a minimal completion against `http://localhost:11434/v1/chat/completions` to confirm the API is live.

**Branch outcomes:**
- Tag present and API responds → proceed to Task 1 as planned.
- Tag absent, Ollama is running → scaffold MCP server in Task 1 with a `TODO(sprint-07): replace model tag once gemma4:26b is indexed by Ollama` comment at the model name constant. Commit as-is and note status DONE_WITH_CONCERNS.
- Ollama not running or GPU unavailable → stop sprint, raise BLOCKED.

**Verify:** Diagnostic output captured. Decision recorded in a one-line comment at the top of `gemma-node/src/index.ts`.

**Commit message:** `chore(gemma-node): record pre-flight diagnostic result`

---

### Task 1 — MCP server scaffold: directory, package, and tsconfig

**What to build:** Create the `legion-swarm/mcp/gemma-node/` package with TypeScript project setup. No implementation yet — just the skeleton that subsequent tasks fill in.

**Files to create:**
- `legion-swarm/mcp/gemma-node/package.json` — name `@legion/gemma-node`, scripts: `build`, `start`, `dev`. Dependencies: `@modelcontextprotocol/sdk`, `node-fetch` (if Node < 18 is in use; otherwise native fetch). Dev dependencies: `typescript`, `@types/node`.
- `legion-swarm/mcp/gemma-node/tsconfig.json` — strict, ESNext target, `outDir: dist`.
- `legion-swarm/mcp/gemma-node/src/index.ts` — empty entry point with the pre-flight comment from Task 0 at line 1.
- `legion-swarm/mcp/gemma-node/.gitignore` — exclude `dist/` and `node_modules/`.

**Verify:** `npm install` and `npm run build` both exit 0 from within the package directory.

**Commit message:** `feat(gemma-node): scaffold MCP package with TypeScript project`

---

### Task 2 — Ollama client module

**What to build:** `legion-swarm/mcp/gemma-node/src/ollama.ts` — a single exported async function that POSTs a prompt to Ollama's OpenAI-compatible completions endpoint and returns plain text.

**Interface the module must expose:**

```ts
export async function callGemma(prompt: string, context?: string): Promise<string>
```

**Behavior:**
- Concatenates `context` (if provided) as a system message before the user prompt.
- Posts to `http://localhost:11434/v1/chat/completions` with `model: "gemma4:26b"` (or the TODO-flagged constant from Task 0 if the tag is not available).
- `stream: false`.
- No auth header — Ollama local requires none.
- Returns the `choices[0].message.content` string.
- Throws a descriptive error on non-200 response or network failure.

**Files to create:**
- `legion-swarm/mcp/gemma-node/src/ollama.ts`

**Verify:** Unit-test the function manually with a short prompt via `npx ts-node src/ollama.ts` invocation or a small `test.ts` scratch file (not committed). Confirm round-trip returns a non-empty string.

**Commit message:** `feat(gemma-node): add Ollama client module`

---

### Task 3 — MCP server: expose `gemma` tool

**What to build:** Wire `callGemma` into an MCP `Server` instance and expose a single `gemma` tool. Complete the `src/index.ts` entry point.

**Tool definition:**

- Name: `gemma`
- Description: "Call the local Gemma 4 26B model for mechanical tasks: boilerplate, docstrings, scaffolding, simple refactors, repetitive transforms."
- Input schema: `{ prompt: string (required), context: string (optional) }`
- Handler: calls `callGemma(prompt, context)`, returns result as plain text content.
- On error: return an error text response — do not throw and crash the server.

**Server setup:**
- Transport: `StdioServerTransport` (agents launch the process and communicate via stdio).
- Server name: `gemma-node`, version from `package.json`.

**Files to modify:**
- `legion-swarm/mcp/gemma-node/src/index.ts` — complete implementation.

**Verify:** `npm run build && node dist/index.js` starts without error. Send a minimal MCP `tools/call` JSON payload via stdin and confirm a valid MCP response comes back on stdout.

**Commit message:** `feat(gemma-node): implement gemma MCP tool over stdio transport`

---

### Task 4 — MCP server README and agent invocation guide

**What to build:** `legion-swarm/mcp/gemma-node/README.md` — short operational reference for agents and humans spinning up the node.

**Sections to include:**
- Prerequisites: Ollama running, `gemma4:26b` pulled.
- Start command: `npm run build && node dist/index.js`.
- Tool signature: `gemma(prompt, context?)` with two short examples.
- Routing guidance (inline summary, not a copy of the full heuristic — that lives in `meta/CLAUDE.md`): "Use for mechanical tasks. Avoid for architecture, debugging, and tasks needing >32k context."
- Known limitation: context window size unconfirmed; do not pass entire codebases.

**Files to create:**
- `legion-swarm/mcp/gemma-node/README.md`

**Verify:** README renders correctly in GitHub Markdown preview. No orphaned headers. Start command matches `package.json` scripts.

**Commit message:** `docs(gemma-node): add README with start instructions and routing summary`

---

### Task 5 — Watchdog: Gemma node health probe

**What to build:** Extend the Watchdog skill with a Gemma node health probe. The probe runs alongside existing context/usage checks and writes Gemma node status into `status.json`.

**Two health signals to add:**

1. **GPU memory pressure** — run `nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits`. Parse used/total. Flag `gemma_gpu_pressure: true` if used/total > 0.90.
2. **Response latency** — send a minimal completion request (`"ping"` prompt) to `http://localhost:11434/v1/chat/completions` and measure wall-clock time. Flag `gemma_latency_ms` in `status.json`. Flag `gemma_node_unreachable: true` if the request fails or times out after 10 seconds.

**`status.json` additions:**

```json
{
  "gemma_node_unreachable": false,
  "gemma_latency_ms": 412,
  "gemma_gpu_pressure": false
}
```

**Reporting to Monday:**
- If `gemma_node_unreachable` is true: append to the watchdog's Monday update for the current session: "Gemma node unreachable."
- If `gemma_gpu_pressure` is true: append "Gemma GPU memory >90%."
- Normal operation: no Monday noise.

**Files to modify:**
- `legion-swarm/skills/watchdog/watchdog-prompt.md` — add Gemma probe step to polling loop (after existing context/usage checks).

**Verify:** Poll loop in `watchdog-prompt.md` now has 3 checks in sequence: context, usage, Gemma node. Monday update logic for Gemma conditions is distinct from the existing graceful/hard-stop logic and does not interfere with it.

**Commit message:** `feat(watchdog): add Gemma node health probe (GPU pressure + latency)`

---

### Task 6 — Routing guidance in `meta/CLAUDE.md`

**What to build:** Add a "Compute Routing" section to `legion-swarm/meta/CLAUDE.md` that gives Legion and all agents clear guidance on when to call `gemma()` vs Claude.

**Section title:** `## Compute Routing — Gemma vs Claude`

**Content:**

Route to `gemma()` (local Gemma 4 26B):
- Boilerplate generation from an explicit spec
- Unit test scaffolding
- Docstring and comment generation
- Simple refactors with step-by-step instructions
- File summarization (single file, not whole codebase)
- Repetitive file transformations (migrate N files to a new pattern)

Keep with Claude:
- Architecture decisions and task decomposition
- Debugging ambiguous or multi-file failures
- Tasks requiring >32k tokens of context
- Any MCP tool chain (git, browser, shell)
- Orchestration logic (Legion itself)
- Tasks where correctness cannot be verified automatically

Practical note: When in doubt, keep it with Claude. Gemma is for offloading volume, not for replacing judgment.

**Files to modify:**
- `legion-swarm/meta/CLAUDE.md`

**Verify:** Section is present, clearly separated from adjacent sections, and uses the exact routing categories from the research doc. No content from existing sections is displaced or duplicated.

**Commit message:** `docs(meta): add compute routing guidance for Gemma vs Claude`

---

## Done Criteria

- [ ] Pre-flight diagnostic run; result recorded; branch outcome determined and followed
- [ ] `legion-swarm/mcp/gemma-node/` builds cleanly and exposes a working `gemma` MCP tool over stdio
- [ ] `callGemma(prompt, context?)` returns plain text from Ollama; error cases handled
- [ ] Watchdog polls GPU memory pressure and Gemma response latency; writes both to `status.json`
- [ ] Watchdog Monday update includes Gemma node warnings when thresholds are hit
- [ ] `meta/CLAUDE.md` has a compute routing section matching the research doc heuristic
- [ ] README covers start command, tool signature, and routing summary

## Out of Scope

- Phase 2 automatic routing (dispatcher classifies tasks and routes without agent decision)
- Structured tool responses from Gemma (function calling) — plain text only in this sprint
- Gemma node in Docker — Ollama only for now
- Context window truncation guard — pending confirmation of Gemma 4 context window size
- Multi-model fallback (Gemma → Claude if Gemma fails) — future sprint
- Gemma node auto-restart if Ollama crashes — future sprint
