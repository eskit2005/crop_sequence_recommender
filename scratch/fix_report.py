with open('/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/bd_100_batches/audit_report_batch02.md') as f:
    text = f.read()

# fix any remaining shell substitutions
text = text.replace('Every single coordinate pair $ resolved', 'Every single coordinate pair (lat, lon) resolved')
text = text.replace('cropping intensity to =2$ (double-cropping)', 'cropping intensity to K=2 (double-cropping)')
text = text.replace('Intensity ($K$)', 'Cropping Intensity (K)')
text = text.replace('Intensity ($)', 'Cropping Intensity (K)')
text = text.replace('Coords $(Lat, Lon)$', 'Coords (Lat, Lon)')
text = text.replace('Coords $', 'Coords (Lat, Lon)')

with open('/Users/ibrahim/.gemini/antigravity/scratch/crop_sequence_recommender/data/bd_100_batches/audit_report_batch02.md', 'w') as f:
    f.write(text)

print('Cleaned audit report successfully.')
