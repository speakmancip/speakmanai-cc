#!/usr/bin/env bash
# install.sh — Install SPEAKMAN.AI skills and supporting assets into Claude Code (macOS / Linux)
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$HOME/.claude/skills"
ASSET_DIR="$HOME/.claude/speakmanai-cc"

mkdir -p "$SKILL_DIR"
mkdir -p "$ASSET_DIR"

# --- Skills ---

SKILLS=("generate-sad" "generate-compliance-report" "generate-speakmanai-workflow")

for skill in "${SKILLS[@]}"; do
    src="$REPO_DIR/.claude/skills/$skill"
    dst="$SKILL_DIR/$skill"

    if [ -d "$dst" ]; then
        echo "Skill already exists: $skill"
        read -p "Overwrite? [y/N]: " confirm
        [[ "$confirm" =~ ^[Yy]$ ]] || { echo "Skipped: $skill"; continue; }
        rm -rf "$dst"
    fi

    cp -r "$src" "$dst"
    echo "OK Skill installed -> $dst"
done

# --- Supporting assets (prompts, scripts, templates) ---

ASSETS=("prompts" "scripts" "templates")

for asset in "${ASSETS[@]}"; do
    src="$REPO_DIR/$asset"
    dst="$ASSET_DIR/$asset"

    if [ -d "$dst" ]; then
        echo "Asset already exists: $asset"
        read -p "Overwrite? [y/N]: " confirm
        [[ "$confirm" =~ ^[Yy]$ ]] || { echo "Skipped: $asset"; continue; }
        rm -rf "$dst"
    fi

    cp -r "$src" "$dst"
    echo "OK Asset installed  -> $dst"
done

# --- puppeteer (PDF generation) ---

echo "Installing puppeteer..."
if cd "$ASSET_DIR" && npm install puppeteer --save > /dev/null 2>&1; then
    echo "OK puppeteer installed"
else
    echo "WARNING: npm install puppeteer failed — PDF generation will be unavailable."
    echo "         To install manually: cd $ASSET_DIR && npm install puppeteer"
fi
cd "$REPO_DIR"

echo ""
echo "Installation complete."
echo "  Skills : $SKILL_DIR"
echo "  Assets : $ASSET_DIR"
echo ""
echo "Usage: open Claude Code in any project directory and run /generate-sad, /generate-compliance-report, or /generate-speakmanai-workflow"
echo "Requires: SPEAKMAN.AI MCP server configured in your Claude Code settings."
echo ""
echo "To use your own branding, add logo.png to: $ASSET_DIR/templates/corporate/"
