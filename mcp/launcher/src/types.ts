import { z } from "zod";

// All 11 agent roles
export type AgentRole =
  | "architect"
  | "planner"
  | "coder"
  | "tester"
  | "debugger"
  | "reviewer"
  | "refactorer"
  | "mapper"
  | "documenter"
  | "frontend"
  | "qa";

export const AGENT_ROLES: AgentRole[] = [
  "architect",
  "planner",
  "coder",
  "tester",
  "debugger",
  "reviewer",
  "refactorer",
  "mapper",
  "documenter",
  "frontend",
  "qa",
];

// Branded string type for terminal IDs
export type TerminalID = string & { readonly __brand: "TerminalID" };

export function makeTerminalID(role: AgentRole): TerminalID {
  return `${role}-${Date.now()}` as TerminalID;
}

// Agent status returned by get_agent_status
export interface AgentStatus {
  terminalId: TerminalID;
  role: AgentRole;
  repo: string;
  lastStatus: "pending" | "DONE" | "DONE_WITH_CONCERNS" | "BLOCKED" | "NEEDS_CONTEXT";
  lastWhat: string | null;
  pingRequired: boolean;
  mapUpdateRequired: boolean;
  lastUpdatedAt: string | null;
}

// Zod schema matching the finalized agent settings JSON
export const AgentSettingsSchema = z.object({
  role: z.enum([
    "architect",
    "planner",
    "coder",
    "tester",
    "debugger",
    "reviewer",
    "refactorer",
    "mapper",
    "documenter",
    "frontend",
    "qa",
  ]),
  skills: z.array(z.string()),
  model: z.string(),
  workingDirectoryStrategy: z.enum(["repo", "swarm-root"]),
  contextBudget: z.number().positive(),
  allowedTools: z.array(z.string()),
  env: z.record(z.string(), z.string()),
});

export type AgentSettings = z.infer<typeof AgentSettingsSchema>;

// Registry entry for a live agent session
export interface RegistryEntry {
  terminalId: TerminalID;
  role: AgentRole;
  repo: string;
  pid: number | undefined;
  spawnedAt: string;
}
