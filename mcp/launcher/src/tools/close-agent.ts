import { execSync } from "child_process";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { z } from "zod";
import * as registry from "../registry.js";
import type { TerminalID } from "../types.js";

export const CloseAgentInputSchema = z.object({
  terminalId: z.string().min(1, "terminalId must be non-empty"),
});

export type CloseAgentInput = z.infer<typeof CloseAgentInputSchema>;

export interface CloseAgentResult {
  closed: boolean;
  terminalId: TerminalID;
  role?: string;
  repo?: string;
  reason?: string;
}

export async function closeAgent(input: CloseAgentInput): Promise<CloseAgentResult> {
  const terminalId = input.terminalId as TerminalID;
  const entry = registry.lookup(terminalId);

  if (!entry) {
    return { closed: false, terminalId, reason: "not_found" };
  }

  // 1. Kill the process gracefully via taskkill (sends WM_CLOSE first)
  if (entry.pid !== undefined) {
    try {
      execSync(`taskkill /PID ${entry.pid} /T`, { stdio: "ignore" });
    } catch {
      // Graceful failed — force kill
      try {
        execSync(`taskkill /PID ${entry.pid} /T /F`, { stdio: "ignore" });
      } catch {
        // Process may have already exited — not fatal
      }
    }
  }

  // 2. Delete temp prompt file
  const promptFile = path.join(os.tmpdir(), `${terminalId}-prompt.txt`);
  if (fs.existsSync(promptFile)) {
    try {
      fs.unlinkSync(promptFile);
    } catch {
      // Non-fatal — temp files will be cleaned up by OS eventually
    }
  }

  // 3. Remove from registry
  registry.remove(terminalId);

  return {
    closed: true,
    terminalId,
    role: entry.role,
    repo: entry.repo,
  };
}
