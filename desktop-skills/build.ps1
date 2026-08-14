# build.ps1 - Package the Desktop skill sources in this folder into upload-ready zips.
#
# Produces:
#   speakmanai-sdlc.zip           - the plugin bundle (all 17 SDLC skills, one upload,
#                                    via Claude Desktop's Cowork -> Settings -> Plugins -> Upload)
#   generate-sad.zip               - standalone single-skill fallback, via
#   generate-compliance-report.zip   Settings -> Skills -> Upload (no Cowork/Plugins needed)
#   generate-speakmanai-code.zip
#   copilot-studio-skills.zip     - all 17 skills repackaged for Microsoft Copilot Studio
#                                    (no .claude-plugin/version.json - Copilot Studio doesn't
#                                    understand the Claude plugin format). See COPILOT_STUDIO.md.
#
# Re-run this after editing anything under desktop-skills/ to refresh the zips.
# Zips are gitignored (desktop-skills/*.zip) - they're build output, not source.

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression
Add-Type -AssemblyName System.IO.Compression.FileSystem

function New-SkillZip {
    param(
        [Parameter(Mandatory)] [string]$SourceDir,   # folder to zip, becomes the zip's root entry
        [Parameter(Mandatory)] [string]$ZipPath
    )
    if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
    $base = Split-Path -Parent $SourceDir
    $zip = [System.IO.Compression.ZipFile]::Open($ZipPath, [System.IO.Compression.ZipArchiveMode]::Create)
    try {
        Get-ChildItem -Path $SourceDir -Recurse -File | ForEach-Object {
            # Forward-slash, root-relative entry names - required for the zip to be read
            # correctly by non-Windows unzip tools (Compress-Archive emits backslashes).
            $relPath = $_.FullName.Substring($base.Length + 1).Replace('\', '/')
            [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, $relPath) | Out-Null
        }
    } finally {
        $zip.Dispose()
    }
    $count = (Get-ChildItem -Path $SourceDir -Recurse -File).Count
    Write-Host "OK  $ZipPath  ($count files)"
}

function New-CopilotStudioBundle {
    param(
        [Parameter(Mandatory)] [string]$SkillsDir,   # org-plugins/speakmanai-sdlc/skills
        [Parameter(Mandatory)] [string[]]$ComplexSkills,  # names needing a per-skill zip, not a loose .md
        [Parameter(Mandatory)] [string]$ZipPath
    )
    $staging = Join-Path ([System.IO.Path]::GetTempPath()) ("copilot-studio-" + [guid]::NewGuid())
    New-Item -ItemType Directory -Path $staging | Out-Null
    try {
        Get-ChildItem -Path $SkillsDir -Directory | ForEach-Object {
            $name = $_.Name
            if ($ComplexSkills -contains $name) {
                New-SkillZip -SourceDir $_.FullName -ZipPath (Join-Path $staging "$name.zip")
            } else {
                Copy-Item -Path (Join-Path $_.FullName "SKILL.md") -Destination (Join-Path $staging "$name.md")
            }
        }
        $instructions = @"
# SPEAKMAN.AI skills for Microsoft Copilot Studio

Copilot Studio's Skills tab has no bulk-import - each item here is uploaded one at a time.

1. Unzip this file locally.
2. In Copilot Studio: your agent -> Skills -> Upload a skill.
3. Drag each ``.md`` file in this folder in individually (14 of these - self-contained,
   single file each).
4. Drag each ``.zip`` file in this folder in individually (3 of these - $($ComplexSkills -join ', ')
   - each bundles a synthesis prompt alongside SKILL.md).
5. Add the SPEAKMAN.AI MCP connector before running any skill. If it's a local server
   (not yet hosted), see COPILOT_STUDIO.md in the source repo for exposing it via a tunnel.

Full details, known gaps, and troubleshooting: COPILOT_STUDIO.md in the speakmanai-cc repo
(desktop-skills/COPILOT_STUDIO.md) - not included in this zip, since it documents the build
process rather than being needed at runtime.
"@
        Set-Content -Path (Join-Path $staging "INSTRUCTIONS.md") -Value $instructions -Encoding utf8

        if (Test-Path $ZipPath) { Remove-Item $ZipPath -Force }
        $zip = [System.IO.Compression.ZipFile]::Open($ZipPath, [System.IO.Compression.ZipArchiveMode]::Create)
        try {
            Get-ChildItem -Path $staging -File | ForEach-Object {
                [System.IO.Compression.ZipFileExtensions]::CreateEntryFromFile($zip, $_.FullName, $_.Name) | Out-Null
            }
        } finally {
            $zip.Dispose()
        }
        $count = (Get-ChildItem -Path $staging -File).Count
        Write-Host "OK  $ZipPath  ($count items - unzip locally, drag each into Copilot Studio)"
    } finally {
        Remove-Item -Path $staging -Recurse -Force
    }
}

$root = $PSScriptRoot

New-SkillZip -SourceDir (Join-Path $root "org-plugins\speakmanai-sdlc") -ZipPath (Join-Path $root "speakmanai-sdlc.zip")
New-SkillZip -SourceDir (Join-Path $root "generate-sad")                -ZipPath (Join-Path $root "generate-sad.zip")
New-SkillZip -SourceDir (Join-Path $root "generate-compliance-report")  -ZipPath (Join-Path $root "generate-compliance-report.zip")
New-SkillZip -SourceDir (Join-Path $root "org-plugins\speakmanai-sdlc\skills\generate-speakmanai-code") -ZipPath (Join-Path $root "generate-speakmanai-code.zip")

New-CopilotStudioBundle `
    -SkillsDir (Join-Path $root "org-plugins\speakmanai-sdlc\skills") `
    -ComplexSkills @("generate-sad", "generate-compliance-report", "generate-speakmanai-code") `
    -ZipPath (Join-Path $root "copilot-studio-skills.zip")

Write-Host ""
Write-Host "Done. See desktop-skills/README.md for how to upload each zip."
