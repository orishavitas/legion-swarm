import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";

const WEBHOOK_URL = process.env.GOOGLE_CHAT_WEBHOOK_URL;
if (!WEBHOOK_URL) {
  console.error("[google-chat] ERROR: GOOGLE_CHAT_WEBHOOK_URL is not set. Exiting.");
  process.exit(1);
}

const server = new Server(
  { name: "legion-swarm/google-chat", version: "0.1.0" },
  { capabilities: { tools: {} } }
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "ping_shepherd",
      description:
        "Send a notification to Shepard-Commander via Google Chat Incoming Webhook. Use when an agent is blocked, needs a decision, or a sprint is complete.",
      inputSchema: {
        type: "object",
        properties: {
          message: { type: "string", description: "The notification body" },
          repo: { type: "string", description: "Repository name" },
          agent: { type: "string", description: "Agent role sending the ping" },
          status: {
            type: "string",
            enum: ["DONE", "BLOCKED", "NEEDS_DECISION"],
            description: "Current status triggering the ping",
          },
          monday_url: {
            type: "string",
            description: "Direct Monday board item URL (optional)",
          },
        },
        required: ["message", "repo", "agent", "status"],
      },
    },
  ],
}));

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  if (name !== "ping_shepherd") {
    return {
      content: [{ type: "text", text: `Unknown tool: ${name}` }],
      isError: true,
    };
  }

  try {
    const { message, repo, agent, status, monday_url } = args as {
      message: string;
      repo: string;
      agent: string;
      status: "DONE" | "BLOCKED" | "NEEDS_DECISION";
      monday_url?: string;
    };

    const lines = [
      `[Legion Swarm] ${repo} — ${agent}`,
      `Status: ${status}`,
      message,
    ];
    if (monday_url) lines.push(`Monday: ${monday_url}`);

    const body = JSON.stringify({ text: lines.join("\n") });

    const response = await fetch(WEBHOOK_URL!, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body,
    });

    if (!response.ok) {
      const errText = await response.text();
      throw new Error(`Webhook POST failed: ${response.status} ${errText}`);
    }

    return {
      content: [{ type: "text", text: JSON.stringify({ ok: true }) }],
    };
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      content: [{ type: "text", text: JSON.stringify({ ok: false, error: message }) }],
      isError: true,
    };
  }
});

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("[google-chat] Server started.");
