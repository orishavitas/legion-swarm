# sync-vault-hard-truths.ps1
# Syncs live hard-truth files from ~/.claude into the legion-wiki Obsidian vault.
# Run this before dispatching a Codex task to ensure the vault is current.
# Can also be wired into a pre-task hook.

param(
    [string]$ClaudeDir = "$env:USERPROFILE\.claude",
    [string]$VaultDir = "G:\Shared drives\R&D Department\AI Research and knowledge base\Obsidian\legion-wiki\03-hard-truths"
)

$ErrorActionPreference = "Stop"

function Sync-File {
    param([string]$Source, [string]$DestName)
    $dest = Join-Path $VaultDir $DestName
    if (Test-Path $Source) {
        Copy-Item -Path $Source -Destination $dest -Force
        Write-Host "  synced: $DestName"
    } else {
        Write-Host "  missing (skipped): $Source"
    }
}

Write-Host "Syncing hard truths to vault..."

# Core quartet files
Sync-File "$ClaudeDir\CLAUDE.md"     "CLAUDE.md"
Sync-File "$ClaudeDir\CHANGELOG.md"  "CHANGELOG.md"
Sync-File "$ClaudeDir\TODO.md"       "TODO.md"

# Memory files — copy all *.md from memory/
$memDir = Join-Path $ClaudeDir "memory"
if (Test-Path $memDir) {
    Get-ChildItem -Path $memDir -Filter "*.md" | ForEach-Object {
        $dest = Join-Path $VaultDir "memory-$($_.Name)"
        Copy-Item -Path $_.FullName -Destination $dest -Force
        Write-Host "  synced: memory-$($_.Name)"
    }
}

Write-Host "Done. Vault hard truths are current."
