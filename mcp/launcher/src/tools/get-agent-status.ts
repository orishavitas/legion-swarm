import { z } from "zod";
import * as registry from "../registry.js";
import type { AgentStatus, SignInStatus, TerminalID } from "../types.js";

export const GetAgentStatusInputSchema = z.object({
  terminalId: z.string().min(1, "terminalId must be non-empty"),
});

export type GetAgentStatusInput = z.infer<typeof GetAgentStatusInputSchema>;

// Parse agent standard report format from Monday update text
function parseStatusUpdate(text: string): Partial<AgentStatus> {
  const result: Partial<AgentStatus> = {};

  // ── Sign-in block ─────────────────────────────────────────────────────────
  // Format: [SIGN-IN] role — repo\nIdentity: LOADED|NOT FOUND\nSkills: ...\nReady: YES|NO
  if (text.includes("[SIGN-IN]")) {
    const readyMatch = text.match(/Ready:\s*(YES|NO)/i);
    if (readyMatch) {
      result.signInStatus = readyMatch[1].toUpperCase() === "YES" ? "confirmed" : "failed";
    }
  }

  // ── Standard status fields (sign-off block or inline update) ─────────────
  const statusMatch = text.match(/\*\*Status:\*\*\s*(DONE_WITH_CONCERNS|DONE|BLOCKED|NEEDS_CONTEXT)/i);
  if (statusMatch) {
    result.lastStatus = statusMatch[1] as AgentStatus["lastStatus"];
  }

  const whatMatch = text.match(/\*\*What:\*\*\s*(.+?)(?:\n|$)/i);
  if (whatMatch) {
    result.lastWhat = whatMatch[1].trim();
  }

  const pingMatch = text.match(/\*\*Ping Shepard-Commander:\*\*\s*(YES|NO)/i);
  if (pingMatch) {
    result.pingRequired = pingMatch[1].toUpperCase() === "YES";
  }

  const mapMatch = text.match(/\*\*Map update needed:\*\*\s*(YES|NO)/i);
  if (mapMatch) {
    result.mapUpdateRequired = mapMatch[1].toUpperCase() === "YES";
  }

  // ── Wiki ingest flag (sign-off only) ─────────────────────────────────────
  const wikiMatch = text.match(/\*\*Wiki ingest needed:\*\*\s*(YES|NO)/i);
  if (wikiMatch) {
    result.wikiIngestRequired = wikiMatch[1].toUpperCase() === "YES";
  }

  return result;
}

export async function getAgentStatus(
  input: GetAgentStatusInput
): Promise<AgentStatus> {
  const terminalId = input.terminalId as TerminalID;
  const entry = registry.lookup(terminalId);

  if (!entry) {
    // Return a structured not-found response rather than throwing
    return {
      terminalId,
      role: "coder", // placeholder — not found
      repo: "",
      signInStatus: "pending",
      lastStatus: "pending",
      lastWhat: null,
      pingRequired: false,
      mapUpdateRequired: false,
      wikiIngestRequired: false,
      lastUpdatedAt: null,
    };
  }

  // Monday MCP integration:
  // The actual Monday board query is performed by Legion (the meta-orchestrator)
  // which has access to Monday MCP tools. This server returns the registry entry
  // and Legion layers Monday data on top.
  //
  // For direct status reads, Legion calls:
  //   mcp__claude_ai_monday_com__get_updates with the board item where
  //   Terminal ID column === terminalId, then passes the text here for parsing.
  //
  // This function is also callable with a pre-fetched update text via the
  // optional mondayUpdateText field (see index.ts tool handler).

  return {
    terminalId,
    role: entry.role,
    repo: entry.repo,
    signInStatus: "pending",
    lastStatus: "pending",
    lastWhat: null,
    pingRequired: false,
    mapUpdateRequired: false,
    wikiIngestRequired: false,
    lastUpdatedAt: null,
  };
}

// Exported so index.ts tool handler can pass Monday update text for parsing
export { parseStatusUpdate };
