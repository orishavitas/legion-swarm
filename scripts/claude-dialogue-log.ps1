# claude-dialogue-log.ps1
# Called by Claude after writing to DIALOGUE.md.
# Reads the latest message and logs it to the Monday board item specified in monday_item_id.
# Also sets TURN.md to the next party.
# Usage: .\scripts\claude-dialogue-log.ps1 -RepoRoot <path> -MondayToken <token>

param(
    [string]$RepoRoot = (Get-Location).Path,
    [string]$MondayToken = $env:MONDAY_API_TOKEN,
    [string]$BoardId = "18408420731"
)

$StateDir = Join-Path $RepoRoot ".codex\state"
$DialogueFile = Join-Path $StateDir "DIALOGUE.md"
$TurnFile = Join-Path $StateDir "TURN.md"

if (-not (Test-Path $DialogueFile)) {
    Write-Error "DIALOGUE.md not found at $DialogueFile"
    exit 1
}

# Parse latest message
$Content = Get-Content $DialogueFile -Raw
$Messages = $Content -split '\[DIALOGUE_END\]' | Where-Object { $_.Trim() }
$Latest = ($Messages | Select-Object -Last 1).Trim()

if (-not $Latest) {
    Write-Host "No messages found in DIALOGUE.md"
    exit 0
}

# Extract header fields
$From      = if ($Latest -match 'from:\s*(\S+)')         { $Matches[1] } else { "unknown" }
$Type      = if ($Latest -match 'type:\s*(\S+)')         { $Matches[1] } else { "unknown" }
$Ref       = if ($Latest -match 'ref:\s*(.+)')           { $Matches[1].Trim() } else { "general" }
$Timestamp = if ($Latest -match 'timestamp:\s*(\S+)')    { $Matches[1] } else { (Get-Date -Format "o") }
$ItemId    = if ($Latest -match 'monday_item_id:\s*(\d+)') { $Matches[1] } else { $null }

# Extract body (after the header block)
$Body = ($Latest -replace '(?s)^---.*?---\s*', '').Trim()
$BodyShort = if ($Body.Length -gt 200) { $Body.Substring(0, 200) + "..." } else { $Body }

# Read current turn
$Turn = if (Test-Path $TurnFile) { (Get-Content $TurnFile -Raw).Trim() } else { "unknown" }

# Build Monday update text
$UpdateText = "[DIALOGUE] from=$From type=$Type ref=$Ref`n$BodyShort`n→ Turn: $Turn"

if (-not $ItemId) {
    Write-Host "No monday_item_id in latest message — skipping Monday log."
    Write-Host "Message parsed: from=$From type=$Type ref=$Ref"
    exit 0
}

if (-not $MondayToken) {
    Write-Host "No MONDAY_API_TOKEN set — skipping Monday log."
    Write-Host "Would have logged to item $ItemId`: $UpdateText"
    exit 0
}

# Post to Monday
$Mutation = "mutation { create_update(item_id: $ItemId, body: ""$($UpdateText -replace '"','\"')"") { id } }"
$Body_Json = @{ query = $Mutation } | ConvertTo-Json -Compress
$Headers = @{ Authorization = $MondayToken; 'Content-Type' = 'application/json' }

try {
    $Response = Invoke-RestMethod -Uri 'https://api.monday.com/v2' -Method Post -Headers $Headers -Body $Body_Json
    Write-Host "Logged to Monday item $ItemId — update id: $($Response.data.create_update.id)"
} catch {
    Write-Host "Monday log failed: $_"
    Write-Host "Message was: $UpdateText"
}
