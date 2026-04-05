import type { AgentRole, RegistryEntry, TerminalID } from "./types.js";

// In-memory map of TerminalID → live session entry
// Source of truth for all active agent sessions within this server process
const sessions = new Map<TerminalID, RegistryEntry>();

export function register(entry: RegistryEntry): void {
  sessions.set(entry.terminalId, entry);
}

export function lookup(terminalId: TerminalID): RegistryEntry | undefined {
  return sessions.get(terminalId);
}

export function remove(terminalId: TerminalID): boolean {
  return sessions.delete(terminalId);
}

export function listAll(): RegistryEntry[] {
  return Array.from(sessions.values());
}

export function listByRole(role: AgentRole): RegistryEntry[] {
  return listAll().filter((e) => e.role === role);
}
