# install.ps1 - Install SPEAKMAN.AI skills and supporting assets into Claude Code (Windows)

$SkillDir  = Join-Path $env:USERPROFILE ".claude\skills"
$AssetDir  = Join-Path $env:USERPROFILE ".claude\speakmanai-cc"

# --- Skills ---

if (-not (Test-Path $SkillDir)) {
    New-Item -ItemType Directory -Path $SkillDir -Force | Out-Null
}

$Skills = Get-ChildItem -Path (Join-Path $PSScriptRoot ".claude\skills") -Directory | ForEach-Object { $_.Name }

foreach ($Skill in $Skills) {
    $Src = Join-Path $PSScriptRoot ".claude\skills\$Skill"
    $Dst = Join-Path $SkillDir $Skill

    if (Test-Path $Dst) {
        Write-Host "Skill already exists: $Skill"
        $confirm = Read-Host "Overwrite? [y/N]"
        if ($confirm -notmatch '^[Yy]$') {
            Write-Host "Skipped: $Skill"
            continue
        }
        Remove-Item -Recurse -Force $Dst
    }

    Copy-Item -Recurse -Path $Src -Destination $Dst -Force
    Write-Host "OK Skill installed -> $Dst"
}

# --- Supporting assets (prompts, scripts, templates) ---

$Assets = @("prompts", "scripts", "templates")

foreach ($Asset in $Assets) {
    $Src = Join-Path $PSScriptRoot $Asset
    $Dst = Join-Path $AssetDir $Asset

    if (Test-Path $Dst) {
        Write-Host "Asset already exists: $Asset"
        $confirm = Read-Host "Overwrite? [y/N]"
        if ($confirm -notmatch '^[Yy]$') {
            Write-Host "Skipped: $Asset"
            continue
        }
        Remove-Item -Recurse -Force $Dst
    }

    Copy-Item -Recurse -Path $Src -Destination $Dst -Force
    Write-Host "OK Asset installed  -> $Dst"
}

# --- puppeteer (PDF generation) ---

Write-Host "Installing puppeteer..."
Push-Location $AssetDir
npm install puppeteer --save 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "OK puppeteer installed"
} else {
    Write-Host "WARNING: npm install puppeteer failed - PDF generation will be unavailable."
    Write-Host "         To install manually: cd $AssetDir && npm install puppeteer"
}
Pop-Location

Write-Host ""
Write-Host "Installation complete."
Write-Host "  Skills : $SkillDir"
Write-Host "  Assets : $AssetDir"
Write-Host ""
Write-Host "Usage: open Claude Code in any project directory and run any installed skill, e.g. /generate-sad"
Write-Host "  New here? See PIPELINE.md in this repo, or run /sdlc-pipeline for a guided walkthrough."
Write-Host "Requires: SPEAKMAN.AI MCP server configured in your Claude Code settings."
Write-Host ""
Write-Host "To use your own branding, add logo.png to: $AssetDir\templates\corporate\"
