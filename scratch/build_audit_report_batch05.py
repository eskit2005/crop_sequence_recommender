import json
import os

batch_file = "/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/bd_100_batches/batch05_southern_coastal.json"
out_report = "/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/bd_100_batches/audit_report_batch05.md"

with open(batch_file) as f:
    locations = json.load(f)

print(f"Loaded {len(locations)} locations.")
