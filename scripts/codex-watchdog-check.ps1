# codex-watchdog-check.ps1
# Run by Codex at Step 0 (before any other work) and optionally between steps.
# Checks for .watchdog/STOP sentinel written by Claude's context-watchdog hook.
# Exit 0 = clear, proceed. Exit 1 = STOP detected, Codex must halt immediately.
# Usage: .\scripts\codex-watchdog-check.ps1 [-RepoRoot <path>]

param(
    [string]$RepoRoot = (Get-Location).Path
)

$SentinelPath = Join-Path $RepoRoot ".watchdog\STOP"

if (Test-Path $SentinelPath) {
    $Content = (Get-Content $SentinelPath -Raw -ErrorAction SilentlyContinue).Trim()
    Write-Host "WATCHDOG STOP detected at: $SentinelPath"
    Write-Host "Reason: $Content"
    Write-Host ""
    Write-Host "Codex must halt immediately:"
    Write-Host "  1. Update sprint task status to 'blocked', blocked_reason='watchdog STOP'"
    Write-Host "  2. Run: .\scripts\codex-handoff.ps1 -TaskId [task_id] -Status blocked -Technical 'Watchdog STOP sentinel detected. No build work performed.' -Summary 'Paused - system-wide usage limit reached. No changes were made.'"
    Write-Host "  3. Emit: LEGION_COMPLETE: status=blocked verification=pending notes='watchdog STOP sentinel - no build work performed'"
    Write-Host "  4. Exit session"
    exit 1
}

Write-Host "WATCHDOG: clear - no STOP sentinel. Proceed with session."
exit 0
