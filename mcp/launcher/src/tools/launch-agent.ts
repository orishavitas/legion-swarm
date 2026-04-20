import { spawn } from "child_process";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { z } from "zod";
import type { RequiredEnv } from "../env.js";
import * as registry from "../registry.js";
import {
  AgentSettingsSchema,
  AGENT_ROLES,
  makeTerminalID,
  type AgentRole,
  type TerminalID,
} from "../types.js";

export const LaunchAgentInputSchema = z.object({
  role: z.enum(AGENT_ROLES as [AgentRole, ...AgentRole[]]),
  repo: z.string().min(1, "repo must be non-empty"),
  task: z.string().min(1, "task must be non-empty"),
});

export type LaunchAgentInput = z.infer<typeof LaunchAgentInputSchema>;

export interface LaunchAgentResult {
  terminalId: TerminalID;
  role: AgentRole;
  repo: string;
  spawnedAt: string;
  signInStatus: "pending" | "confirmed" | "failed" | "timeout";
  signInWarning: string | null;
}

export async function launchAgent(
  input: LaunchAgentInput,
  env: RequiredEnv
): Promise<LaunchAgentResult> {
  const { role, repo, task } = input;

  // 1. Read agent identity file
  const identityPath = path.join(env.LEGION_SWARM_ROOT, "agents", `${role}.md`);
  if (!fs.existsSync(identityPath)) {
    throw new Error(`Agent identity file not found: ${identityPath}`);
  }
  const identityText = fs.readFileSync(identityPath, "utf8");

  // 2. Read and validate settings
  const settingsPath = path.join(
    env.LEGION_SWARM_ROOT,
    "agents",
    "settings",
    `${role}-settings.json`
  );
  if (!fs.existsSync(settingsPath)) {
    throw new Error(`Agent settings file not found: ${settingsPath}`);
  }
  const settingsRaw = JSON.parse(fs.readFileSync(settingsPath, "utf8"));
  const settings = AgentSettingsSchema.parse(settingsRaw);

  // 3. Resolve repo path
  const repoPath = path.join(env.LEGION_SWARM_REPOS_ROOT, repo);

  // 4. Determine working directory from strategy
  const workingDir =
    settings.workingDirectoryStrategy === "swarm-root"
      ? env.LEGION_SWARM_ROOT
      : repoPath;

  // 5. Construct prompt: identity + task
  const prompt =
    identityText +
    `\n\n## Your Task\n\n${task}\n\n## Repo\n\nWorking repo: \`${repo}\`\nPath: \`${workingDir}\`\n`;

  // 6. Write prompt to temp file — avoids Windows shell escaping
  const terminalId = makeTerminalID(role);
  const promptFile = path.join(os.tmpdir(), `${terminalId}-prompt.txt`);
  fs.writeFileSync(promptFile, prompt, "utf8");

  // 7. Build and spawn wt.exe command
  // cmd /k keeps the terminal open after Claude exits so Shepard-Commander can follow the session
  const wtArgs = [
    "new-tab",
    "--title",
    role,
    "--startingDirectory",
    workingDir,
    "cmd",
    "/k",
    "claude",
    "--model",
    settings.model,
    "--print",
    promptFile,
  ];

  const child = spawn("wt.exe", wtArgs, {
    detached: true,
    stdio: "ignore",
    windowsHide: false,
  });
  child.unref();

  const spawnedAt = new Date().toISOString();

  // 8. Register session in memory
  registry.register({
    terminalId,
    role,
    repo,
    pid: child.pid,
    spawnedAt,
  });

  // 9. Fire-and-forget Monday board write (don't await — don't block launch)
  // Monday MCP is called by Legion, not directly from this server.
  // The terminalId is returned so Legion can write it to Monday.

  return {
    terminalId,
    role,
    repo,
    spawnedAt,
    signInStatus: "pending",
    signInWarning:
      "Agent spawned. Verify sign-in via get_agent_status(terminalId, mondayUpdateText) within 60s. If no [SIGN-IN] Monday update appears, agent may not have loaded identity/skills.",
  };
}
