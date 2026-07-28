# build.ps1 - Package the Desktop skill sources in this folder into upload-ready zips.
#
# Produces:
#   speakmanai-sdlc.zip           - the plugin bundle (all 14 SDLC skills, one upload,
#                                    via Claude Desktop's Cowork -> Settings -> Plugins -> Upload)
#   generate-sad.zip               - standalone single-skill fallback, via
#   generate-compliance-report.zip   Settings -> Skills -> Upload (no Cowork/Plugins needed)
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

$root = $PSScriptRoot

New-SkillZip -SourceDir (Join-Path $root "org-plugins\speakmanai-sdlc") -ZipPath (Join-Path $root "speakmanai-sdlc.zip")
New-SkillZip -SourceDir (Join-Path $root "generate-sad")                -ZipPath (Join-Path $root "generate-sad.zip")
New-SkillZip -SourceDir (Join-Path $root "generate-compliance-report")  -ZipPath (Join-Path $root "generate-compliance-report.zip")

Write-Host ""
Write-Host "Done. See desktop-skills/README.md for how to upload each zip."
