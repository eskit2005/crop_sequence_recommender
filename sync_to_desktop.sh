#!/usr/bin/env bash
# ==============================================================================
# Script: sync_to_desktop.sh
# Purpose: Copies ONLY the new, verified Evaluator Decision Support System (DSS)
#          files into your Desktop repository without modifying or moving
#          any existing recommender files.
# ==============================================================================

set -e

SOURCE="/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender"
TARGET="/Users/ibrahim/Desktop/crop_sequence_recommender"

echo "=============================================================================="
echo "🌾 Syncing Evaluator DSS to Desktop: $TARGET"
echo "=============================================================================="

if [ ! -d "$TARGET" ]; then
    echo "Creating target directory: $TARGET"
    mkdir -p "$TARGET"
fi

# 1. Copy the isolated Evaluator engine package and CLI tool into src/
echo "➜ Adding src/evaluator/ and src/evaluate_sequence_cli.py..."
mkdir -p "$TARGET/src"
cp -r "$SOURCE/src/evaluator" "$TARGET/src/"
cp "$SOURCE/src/evaluate_sequence_cli.py" "$TARGET/src/"

# 2. Copy the standalone Evaluator unit tests into tests/
echo "➜ Adding tests/test_evaluator_stages.py..."
mkdir -p "$TARGET/tests"
cp "$SOURCE/tests/test_evaluator_stages.py" "$TARGET/tests/"

# 3. Copy the Evaluator architecture documentation into docs/
echo "➜ Adding docs/crop_sequence_evaluator_architecture.md..."
mkdir -p "$TARGET/docs"
cp "$SOURCE/docs/crop_sequence_evaluator_architecture.md" "$TARGET/docs/"

# 4. Copy the 20-place evaluation script and audit datasets into scripts/ and data/
echo "➜ Adding scripts/evaluate_20_bd_locations.py and data/evaluator_*..."
mkdir -p "$TARGET/scripts" "$TARGET/data"
cp "$SOURCE/scripts/evaluate_20_bd_locations.py" "$TARGET/scripts/"
cp "$SOURCE/data/evaluator_"* "$TARGET/data/"
cp "$SOURCE/data/nasa_power_cache.json" "$TARGET/data/"

echo "=============================================================================="
echo "✓ Sync complete! Evaluator DSS is cleanly installed in your Desktop folder."
echo "  None of your teammates' existing recommender files were touched."
echo "=============================================================================="
