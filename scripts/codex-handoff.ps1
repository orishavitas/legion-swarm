# codex-handoff.ps1
# Run from repo root at Codex session end, whether done, failed, or blocked.
# Writes:
# - .codex/state/HANDOFF_[timestamp].md for Legion audit
# - .codex/state/MONDAY_UPDATE.md for Legion to post to Monday

param(
    [string]$TaskId = "unknown",
    [ValidateSet("passed", "failed", "blocked")]
    [string]$Status = "blocked",
    [string]$Technical = "Not provided.",
    [string]$Summary = "Not provided."
)

$ErrorActionPreference = "Stop"

$StateDir = ".codex\state"
New-Item -ItemType Directory -Force -Path $StateDir | Out-Null

foreach ($file in @("TASK_STATE.md", "LAST_RUN.md", "DECISIONS.md")) {
    $path = Join-Path $StateDir $file
    if (-not (Test-Path $path)) {
        New-Item -ItemType File -Path $path | Out-Null
    }
}

$Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$TimestampIso = Get-Date -Format "o"
$HandoffOut = Join-Path $StateDir "HANDOFF_$Timestamp.md"
$MondayOut = Join-Path $StateDir "MONDAY_UPDATE.md"
$GitArgs = @("-c", "core.excludesFile=")

$TaskState = if (Test-Path "$StateDir\TASK_STATE.md") {
    Get-Content "$StateDir\TASK_STATE.md" -Raw
} else {
    "Not recorded."
}

$LastRun = if (Test-Path "$StateDir\LAST_RUN.md") {
    Get-Content "$StateDir\LAST_RUN.md" -Raw
} else {
    "Not recorded."
}

# Git read-only probes: use Continue so workstation warnings (permission-denied dirs,
# unreadable global ignore) don't abort the handoff write under Stop mode.
$ErrorActionPreference = "Continue"
$Branch = (git @GitArgs branch --show-current 2>$null) | Select-Object -First 1
if (-not $Branch) { $Branch = "unknown" }

$DirtyFiles = @(git @GitArgs status --short 2>$null | Where-Object { $_ -notmatch '^warning:' })
if ($DirtyFiles.Count -eq 0) {
    $DirtyFilesText = "(clean)"
} else {
    $DirtyFilesText = $DirtyFiles -join "`n"
}

$RecentCommits = @(git @GitArgs log --oneline -5 2>$null | Where-Object { $_ -notmatch '^warning:' })
if ($RecentCommits.Count -eq 0) {
    $RecentCommitsText = "(no commits)"
} else {
    $RecentCommitsText = $RecentCommits -join "`n"
}
$ErrorActionPreference = "Stop"

@"
# Agent Handoff - $Timestamp

Task: $TaskId
Status: $Status
Generated: $TimestampIso

## Current objective
$TaskState

## Repo state

Branch: $Branch

Dirty files:
$DirtyFilesText

## Recent commits
$RecentCommitsText

## Last run
$LastRun

## Stop conditions
- Usage is low.
- Tests fail twice for unclear reasons.
- Product or architecture decision is needed.
- Unrelated dirty files are present.
- git push --dry-run fails.
"@ | Set-Content -Path $HandoffOut -Encoding UTF8

@"
# Monday Update - $TaskId

Status: $Status
Generated: $TimestampIso

**[TECHNICAL]**
$Technical

**[SUMMARY]**
$Summary
"@ | Set-Content -Path $MondayOut -Encoding UTF8

Write-Host "Wrote $HandoffOut"
Write-Host "Wrote $MondayOut"
