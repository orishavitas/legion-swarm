# legion-swarm-google-chat MCP Server

Sends notifications to Shepard-Commander via Google Chat Incoming Webhook.

## Setup

### 1. Get a Google Chat Incoming Webhook URL

1. Open the Google Chat space where you want notifications
2. Click the space name → **Apps & integrations** → **Webhooks**
3. Click **Add Webhook**, name it "Legion Swarm", copy the URL

### 2. Set the environment variable

```bash
export GOOGLE_CHAT_WEBHOOK_URL="https://chat.googleapis.com/v1/spaces/..."
```

Or add it to the MCP server's env config (see `.mcp.json`).

### 3. Register the server in Claude Code

See `.mcp.json` at the repo root — the entry is already configured. Set `GOOGLE_CHAT_WEBHOOK_URL` in your environment or Claude Code settings before starting a Legion session.

## Build

```bash
cd mcp/google-chat
npm install
npm run build
```

## Tool: `ping_shepherd`

Sends a formatted notification to Shepard-Commander.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `message` | string | yes | Notification body |
| `repo` | string | yes | Repository name |
| `agent` | string | yes | Agent role |
| `status` | DONE \| BLOCKED \| NEEDS_DECISION | yes | Current status |
| `monday_url` | string | no | Monday board item URL |
