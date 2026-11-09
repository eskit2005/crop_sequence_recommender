import json
import os

batch_file = "/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/bd_100_batches/batch04_northeast_haor.json"
out_file = "/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/bd_100_batches/audit_report_batch04.md"

with open(batch_file) as f:
    data = json.load(f)

# Verification checks
print(f"Loaded {len(data)} locations.")
