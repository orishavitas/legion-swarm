import { launchAgent } from "./dist/tools/launch-agent.js";
import { closeAgent } from "./dist/tools/close-agent.js";
import * as registry from "./dist/registry.js";
import path from "path";
import process from "process";

// Set required env vars
process.env.LEGION_SWARM_ROOT = "C:/Users/OriShavit/Documents/GitHub/legion-swarm";
process.env.LEGION_SWARM_REPOS_ROOT = "C:/Users/OriShavit/repos";

const env = {
  LEGION_SWARM_ROOT: process.env.LEGION_SWARM_ROOT,
  LEGION_SWARM_REPOS_ROOT: process.env.LEGION_SWARM_REPOS_ROOT,
};

async function test() {
  console.log("Starting smoke test...");

  // 1. Launch coder agent
  console.log("Launching 'coder' for repo 'legion-swarm'...");
  const launchResult = await launchAgent(
    {
      role: "coder",
      repo: "legion-swarm",
      task: "Smoke test - just read README.md and report DONE.",
    },
    env
  );

  console.log("Launch result:", JSON.stringify(launchResult, null, 2));
  const { terminalId } = launchResult;

  // 2. Check registry
  const entry = registry.lookup(terminalId);
  console.log("Registry entry:", JSON.stringify(entry, null, 2));

  if (!entry) {
    throw new Error("Registry entry NOT found!");
  }

  // 3. Wait a bit for WT to open
  console.log("Waiting 5 seconds for Windows Terminal to open...");
  await new Promise((resolve) => setTimeout(resolve, 5000));

  // 4. Close agent
  console.log("Closing agent...");
  const closeResult = await closeAgent({ terminalId });
  console.log("Close result:", JSON.stringify(closeResult, null, 2));

  // 5. Check registry again
  const finalEntry = registry.lookup(terminalId);
  console.log("Final registry entry:", finalEntry ? "STILL EXISTS (ERROR)" : "CLEANED UP (OK)");

  console.log("Smoke test complete.");
}

test().catch((err) => {
  console.error("Smoke test FAILED:", err);
  process.exit(1);
});
