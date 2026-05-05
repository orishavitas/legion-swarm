# codex-dialogue-check.ps1
# Run by Codex at session start and between tasks.
# Reads TURN.md — if "codex", reads latest DIALOGUE.md message and prints it.
# Codex uses the output to know what to respond to.
# Usage: .\scripts\codex-dialogue-check.ps1

param(
    [string]$RepoRoot = (Get-Location).Path
)

$StateDir = Join-Path $RepoRoot ".codex\state"
$TurnFile = Join-Path $StateDir "TURN.md"
$DialogueFile = Join-Path $StateDir "DIALOGUE.md"

if (-not (Test-Path $TurnFile)) {
    Write-Host "TURN: unset — no dialogue active. Proceeding with sprint task."
    exit 0
}

$Turn = (Get-Content $TurnFile -Raw).Trim().ToLower()

if ($Turn -eq "claude") {
    Write-Host "TURN: claude — Claude must act before Codex. Read DIALOGUE.md for context, then wait."
    Write-Host ""
    if (Test-Path $DialogueFile) {
        $Content = Get-Content $DialogueFile -Raw
        $LastMessage = ($Content -split '\[DIALOGUE_END\]' | Where-Object { $_.Trim() } | Select-Object -Last 1).Trim()
        Write-Host "=== Last message in dialogue ==="
        Write-Host $LastMessage
    }
    exit 1
}

if ($Turn -eq "codex") {
    Write-Host "TURN: codex — Your turn. Reading latest message."
    Write-Host ""
    if (-not (Test-Path $DialogueFile)) {
        Write-Host "DIALOGUE.md not found. Nothing to respond to."
        exit 0
    }

    $Content = Get-Content $DialogueFile -Raw
    $Messages = $Content -split '\[DIALOGUE_END\]' | Where-Object { $_.Trim() }
    $Latest = $Messages | Select-Object -Last 1

    Write-Host "=== Message to respond to ==="
    Write-Host $Latest.Trim()
    Write-Host ""
    Write-Host "After responding: append your message to DIALOGUE.md, set TURN.md to 'claude', commit + push."
    exit 0
}

Write-Host "TURN: '$Turn' — unrecognized value. Check .codex/state/TURN.md"
exit 1
