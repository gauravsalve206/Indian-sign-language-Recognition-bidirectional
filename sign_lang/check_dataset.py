"""
Quick script to check dataset statistics.
Run: python check_dataset.py
"""
from pathlib import Path
from collections import Counter
import numpy as np

from src import config
from src.utils.data_utils import load_dataset

X, y, idx_to_label = load_dataset()

print("\n=== Dataset Statistics ===")
label_counts = Counter(y)
total = len(X)

for idx, label in sorted(idx_to_label.items()):
    count = label_counts.get(idx, 0)
    pct = (count / total * 100) if total > 0 else 0
    print(f"  {label:15s}: {count:4d} samples ({pct:5.1f}%)")

print(f"\nTotal: {total} samples")
print(f"Classes: {len(idx_to_label)}")
print(f"Average per class: {total / len(idx_to_label):.1f}")

# Check for imbalance
if len(label_counts) > 1:
    counts = list(label_counts.values())
    max_count = max(counts)
    min_count = min(counts)
    ratio = max_count / min_count if min_count > 0 else float('inf')
    print(f"\nClass imbalance ratio: {ratio:.1f}x (max/min)")
    if ratio > 2:
        print("  ⚠️  WARNING: Severe class imbalance detected!")
        print("  Recommendation: Collect more data for minority classes")














