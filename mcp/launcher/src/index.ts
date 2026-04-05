import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { validateEnv } from "./env.js";
import { parseStatusUpdate } from "./tools/get-agent-status.js";
import { launchAgent, LaunchAgentInputSchema } from "./tools/launch-agent.js";
import { closeAgent, CloseAgentInputSchema } from "./tools/close-agent.js";
import { GetAgentStatusInputSchema } from "./tools/get-agent-status.js";
import * as registry from "./registry.js";
import type { TerminalID, AgentStatus } from "./types.js";

// Fail fast at startup if required env vars are missing
const env = validateEnv();

const server = new Server(
  {
    name: "legion-swarm/launcher-mcp",
    version: "0.1.0",
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// ─── tools/list ──────────────────────────────────────────────────────────────

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: "launch_agent",
      description:
        "Spawn a Windows Terminal tab with a Legion Swarm agent. Injects agent identity and task as initial prompt. Returns terminalId for tracking.",
      inputSchema: {
        type: "object",
        properties: {
          role: {
            type: "string",
            enum: [
              "architect","planner","coder","tester","debugger",
              "reviewer","refactorer","mapper","documenter","frontend","qa",
            ],
            description: "Agent role to spawn",
          },
          repo: {
            type: "string",
            description: "Repository name (relative to LEGION_SWARM_REPOS_ROOT)",
          },
          task: {
            type: "string",
            description: "Task description injected as the agent's initial prompt",
          },
        },
        required: ["role", "repo", "task"],
      },
    },
    {
      name: "get_agent_status",
      description:
        "Read the latest status for an agent session. Returns parsed report fields from the registry and any provided Monday update text.",
      inputSchema: {
        type: "object",
        properties: {
          terminalId: {
            type: "string",
            description: "Terminal ID returned by launch_agent",
          },
          mondayUpdateText: {
            type: "string",
            description:
              "Optional: raw Monday board update text to parse into structured fields",
          },
        },
        required: ["terminalId"],
      },
    },
    {
      name: "close_agent",
      description:
        "Close a running agent terminal session. Kills the process, deletes the temp prompt file, and removes the registry entry.",
      inputSchema: {
        type: "object",
        properties: {
          terminalId: {
            type: "string",
            description: "Terminal ID returned by launch_agent",
          },
        },
        required: ["terminalId"],
      },
    },
  ],
}));

// ─── tools/call ──────────────────────────────────────────────────────────────

server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  try {
    switch (name) {
      case "launch_agent": {
        const input = LaunchAgentInputSchema.parse(args);
        const result = await launchAgent(input, env);
        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      }

      case "get_agent_status": {
        const rawInput = GetAgentStatusInputSchema.parse(args);
        const terminalId = rawInput.terminalId as TerminalID;
        const entry = registry.lookup(terminalId);

        if (!entry) {
          const notFound: AgentStatus = {
            terminalId,
            role: "coder",
            repo: "",
            lastStatus: "pending",
            lastWhat: null,
            pingRequired: false,
            mapUpdateRequired: false,
            lastUpdatedAt: null,
          };
          return {
            content: [{ type: "text", text: JSON.stringify({ ...notFound, error: "not_found" }, null, 2) }],
          };
        }

        // Parse Monday update text if provided
        const mondayText = (args as Record<string, unknown>)?.mondayUpdateText as string | undefined;
        const parsed = mondayText ? parseStatusUpdate(mondayText) : {};

        const status: AgentStatus = {
          terminalId,
          role: entry.role,
          repo: entry.repo,
          lastStatus: parsed.lastStatus ?? "pending",
          lastWhat: parsed.lastWhat ?? null,
          pingRequired: parsed.pingRequired ?? false,
          mapUpdateRequired: parsed.mapUpdateRequired ?? false,
          lastUpdatedAt: mondayText ? new Date().toISOString() : null,
        };

        return {
          content: [{ type: "text", text: JSON.stringify(status, null, 2) }],
        };
      }

      case "close_agent": {
        const input = CloseAgentInputSchema.parse(args);
        const result = await closeAgent(input);
        return {
          content: [{ type: "text", text: JSON.stringify(result, null, 2) }],
        };
      }

      default:
        return {
          content: [{ type: "text", text: `Unknown tool: ${name}` }],
          isError: true,
        };
    }
  } catch (err) {
    const message = err instanceof Error ? err.message : String(err);
    return {
      content: [
        {
          type: "text",
          text: JSON.stringify({ code: "TOOL_ERROR", message }, null, 2),
        },
      ],
      isError: true,
    };
  }
});

// ─── Start ───────────────────────────────────────────────────────────────────

const transport = new StdioServerTransport();
await server.connect(transport);
console.error("[launcher-mcp] Server started. Listening on stdio.");
