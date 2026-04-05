// Validate required environment variables at startup.
// Throws with a clear message if any are missing — fail fast, not at tool call time.

const REQUIRED_ENV_VARS = ["LEGION_SWARM_ROOT", "LEGION_SWARM_REPOS_ROOT"] as const;

export type RequiredEnv = {
  LEGION_SWARM_ROOT: string;
  LEGION_SWARM_REPOS_ROOT: string;
};

export function validateEnv(): RequiredEnv {
  const missing: string[] = [];

  for (const key of REQUIRED_ENV_VARS) {
    if (!process.env[key]) {
      missing.push(key);
    }
  }

  if (missing.length > 0) {
    console.error(
      `[launcher-mcp] FATAL: Missing required environment variables:\n` +
        missing.map((k) => `  - ${k}`).join("\n") +
        `\n\nSet them before starting the server:\n` +
        `  export LEGION_SWARM_ROOT=/absolute/path/to/legion-swarm\n` +
        `  export LEGION_SWARM_REPOS_ROOT=/absolute/path/to/repos\n`
    );
    process.exit(1);
  }

  return {
    LEGION_SWARM_ROOT: process.env.LEGION_SWARM_ROOT!,
    LEGION_SWARM_REPOS_ROOT: process.env.LEGION_SWARM_REPOS_ROOT!,
  };
}
