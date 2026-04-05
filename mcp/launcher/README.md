# @legion-swarm/launcher-mcp

MCP server that spawns, monitors, and closes Legion Swarm agent terminal sessions in Windows Terminal.

## Required Environment Variables

| Variable | Description |
|----------|-------------|
| `LEGION_SWARM_ROOT` | Absolute path to the `legion-swarm` repo root |
| `LEGION_SWARM_REPOS_ROOT` | Absolute path to the directory containing all managed repos |

The server **exits with code 1** at startup if either variable is missing.

## Registering in Claude Code Settings

Add to your Claude Code MCP server configuration (`.claude/settings.json` or global settings):

```json
{
  "mcpServers": {
    "launcher": {
      "command": "node",
      "args": ["C:/Users/OriShavit/repos/legion-swarm/mcp/launcher/dist/index.js"],
      "env": {
        "LEGION_SWARM_ROOT": "C:/Users/OriShavit/repos/legion-swarm",
        "LEGION_SWARM_REPOS_ROOT": "C:/Users/OriShavit/repos"
      }
    }
  }
}
```

For development (tsx, no build required):

```json
{
  "mcpServers": {
    "launcher": {
      "command": "npx",
      "args": ["tsx", "C:/Users/OriShavit/repos/legion-swarm/mcp/launcher/src/index.ts"],
      "env": {
        "LEGION_SWARM_ROOT": "C:/Users/OriShavit/repos/legion-swarm",
        "LEGION_SWARM_REPOS_ROOT": "C:/Users/OriShavit/repos"
      }
    }
  }
}
```

## Tools

### `launch_agent(role, repo, task)`

Spawns a Windows Terminal tab with a Claude Code session for the given agent role.

- Reads agent identity from `agents/{role}.md`
- Reads agent settings from `agents/settings/{role}-settings.json`
- Writes the prompt to a temp file (avoids Windows escaping hell)
- Spawns `wt.exe` detached — Launcher does not block
- Returns `terminalId` for subsequent status/close calls

**Example:**
```json
{
  "role": "coder",
  "repo": "my-app",
  "task": "Implement the login form per the spec in tasks/todo.md"
}
```

**Returns:**
```json
{
  "terminalId": "coder-1712345678901",
  "role": "coder",
  "repo": "my-app",
  "spawnedAt": "2026-04-05T20:00:00.000Z"
}
```

### `get_agent_status(terminalId, mondayUpdateText?)`

Reads the registry entry for a terminal session and optionally parses a Monday board update.

- Returns `{ lastStatus: "pending" }` if no update text provided yet
- Pass `mondayUpdateText` (fetched from Monday MCP by Legion) to get parsed fields

**Example:**
```json
{
  "terminalId": "coder-1712345678901",
  "mondayUpdateText": "**Status:** DONE\n**What:** Implemented login form\n**Files:** src/login.tsx\n**Map update needed:** NO\n**Ping Shepard-Commander:** NO"
}
```

**Returns:**
```json
{
  "terminalId": "coder-1712345678901",
  "role": "coder",
  "repo": "my-app",
  "lastStatus": "DONE",
  "lastWhat": "Implemented login form",
  "pingRequired": false,
  "mapUpdateRequired": false,
  "lastUpdatedAt": "2026-04-05T21:00:00.000Z"
}
```

### `close_agent(terminalId)`

Closes the terminal session identified by `terminalId`.

- Sends `taskkill /PID {pid} /T` (graceful) then `/F` if needed
- Deletes temp prompt file from `os.tmpdir()`
- Removes entry from in-memory registry

**Example:**
```json
{ "terminalId": "coder-1712345678901" }
```

**Returns:**
```json
{
  "closed": true,
  "terminalId": "coder-1712345678901",
  "role": "coder",
  "repo": "my-app"
}
```

## Building

```bash
npm install
npm run build   # outputs to dist/
```

## Development

```bash
LEGION_SWARM_ROOT=/path/to/legion-swarm \
LEGION_SWARM_REPOS_ROOT=/path/to/repos \
npx tsx src/index.ts
```
