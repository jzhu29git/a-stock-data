param(
    [string]$Python = "C:\Program Files\Python312\python.exe",
    [string]$CodexSkillsDir = "$env:USERPROFILE\.codex\skills"
)

$ErrorActionPreference = "Stop"

$repoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$skillhubSource = Join-Path $PSScriptRoot "skillhub\iwencai-skillhub-cli"
$announcementSource = Join-Path $PSScriptRoot "skillhub\announcement-search"

$skillhubHome = Join-Path $env:USERPROFILE ".iwencai-skillhub"
$localBin = Join-Path $env:USERPROFILE ".local\bin"
$announcementTarget = Join-Path $CodexSkillsDir "announcement-search"

New-Item -ItemType Directory -Force -Path $skillhubHome, $localBin, $CodexSkillsDir | Out-Null
Copy-Item -LiteralPath (Join-Path $skillhubSource "aime_skillhub_cli.py") -Destination (Join-Path $skillhubHome "aime_skillhub_cli.py") -Force
Copy-Item -LiteralPath (Join-Path $skillhubSource "cli") -Destination (Join-Path $skillhubHome "cli") -Recurse -Force

$cmdWrapper = Join-Path $localBin "iwencai-skillhub-cli.cmd"
@"
@echo off
"$Python" "%USERPROFILE%\.iwencai-skillhub\aime_skillhub_cli.py" %*
"@ | Set-Content -Path $cmdWrapper -Encoding ASCII

if (Test-Path $announcementTarget) {
    Remove-Item -Recurse -Force $announcementTarget
}
Copy-Item -LiteralPath $announcementSource -Destination $announcementTarget -Recurse -Force

& $Python (Join-Path $repoRoot "codex\patch_announcement_search.py")

Write-Host "Installed iwencai SkillHub CLI wrapper: $cmdWrapper"
Write-Host "Installed announcement-search skill: $announcementTarget"
