import { execSync } from "child_process";
import * as fs from "fs";
import * as os from "os";
import * as path from "path";
import { z } from "zod";
import * as registry from "../registry.js";
import type { TerminalID } from "../types.js";
import { parseStatusUpdate } from "./get-agent-status.js";

export const CloseAgentInputSchema = z.object({
  terminalId: z.string().min(1, "terminalId must be non-empty"),
  mondayUpdateText: z.string().optional(),
});

export type CloseAgentInput = z.infer<typeof CloseAgentInputSchema>;

export interface CloseAgentResult {
  terminalId: string;
  closed: boolean;
  signOffVerified: boolean;
  warning: string | null;
}

export async function closeAgent(input: CloseAgentInput): Promise<CloseAgentResult> {
  const terminalId = input.terminalId as TerminalID;
  const entry = registry.lookup(terminalId);

  if (!entry) {
    return { terminalId: input.terminalId, closed: false, signOffVerified: false, warning: "not_found" };
  }

  // Verify sign-off format before closing
  let signOffVerified = false;
  let warning: string | null = null;

  if (input.mondayUpdateText) {
    const parsed = parseStatusUpdate(input.mondayUpdateText);
    const hasStatus = parsed.lastStatus && parsed.lastStatus !== "pending";
    if (!hasStatus) {
      warning =
        `[SIGN-OFF WARNING] No valid Status field found in Monday update for ${input.terminalId}. ` +
        `Expected: **Status:** DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT. ` +
        `Closing anyway — but Shepard-Commander should be notified.`;
    } else {
      signOffVerified = true;
    }
  } else {
    warning =
      `[SIGN-OFF WARNING] No Monday update text provided for ${input.terminalId}. ` +
      `Cannot verify sign-off. Pass mondayUpdateText to close_agent to enable verification.`;
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
    terminalId: input.terminalId,
    closed: true,
    signOffVerified,
    warning,
  };
}
