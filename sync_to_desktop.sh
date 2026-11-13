#!/usr/bin/env bash
# ==============================================================================
# Script: sync_to_desktop.sh
# Purpose: Copies the complete, verified Evaluator Decision Support System (DSS)
#          from the Gemini environment to your local Desktop repository.
# ==============================================================================

set -e

SOURCE_DIR="/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender"
TARGET_DIR="/Users/ibrahim/Desktop/crop_sequence_recommender"

echo "=============================================================================="
echo "🌾 Syncing Evaluator DSS to Desktop: $TARGET_DIR"
echo "=============================================================================="

if [ ! -d "$TARGET_DIR" ]; then
    echo "Creating target directory: $TARGET_DIR"
    mkdir -p "$TARGET_DIR"
fi

rsync -av \
  --exclude='.git' \
  --exclude='__pycache__' \
  --exclude='*.pyc' \
  "$SOURCE_DIR/" "$TARGET_DIR/"

echo "=============================================================================="
echo "✓ Sync complete! Your Desktop folder now has the full Evaluator DSS structure."
echo "=============================================================================="
