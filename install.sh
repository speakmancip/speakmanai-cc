#!/usr/bin/env bash
# install.sh — Install SPEAKMAN.AI skills and supporting assets into Claude Code (macOS / Linux)
set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$HOME/.claude/skills"
ASSET_DIR="$HOME/.claude/speakmanai-cc"

mkdir -p "$SKILL_DIR"
mkdir -p "$ASSET_DIR"

# --- Skills ---

SKILLS=()
for d in "$REPO_DIR"/.claude/skills/*/; do
    SKILLS+=("$(basename "$d")")
done

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

# --- Supporting assets (synthesis prompts, HTML renderer) ---

ASSETS=("prompts" "scripts")

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

echo ""
echo "Installation complete."
echo "  Skills : $SKILL_DIR"
echo "  Assets : $ASSET_DIR"
echo ""
echo "Usage: open Claude Code in any project directory and run any installed skill, e.g. /generate-sad"
echo "  New here? See PIPELINE.md in this repo, or run /sdlc-pipeline for a guided walkthrough."
echo "Requires: SPEAKMAN.AI MCP server registered with Claude Code (claude mcp add)."
