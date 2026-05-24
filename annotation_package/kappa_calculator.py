"""
Cohen's Kappa Calculator
========================
Run after BOTH annotators complete their sheets:

    python annotation_package/kappa_calculator.py

Reads annotation_sheet_A1.xlsx and annotation_sheet_A2.xlsx,
computes Cohen's Kappa, and prints a full agreement report.
"""

from pathlib import Path
import sys

try:
    import openpyxl
    from sklearn.metrics import cohen_kappa_score, confusion_matrix, classification_report
    import pandas as pd
    import numpy as np
except ImportError:
    print("Install dependencies: pip install openpyxl scikit-learn pandas --break-system-packages")
    sys.exit(1)

BASE = Path(__file__).parent

def load_labels(path, col_idx=4):  # col E = index 4 (0-based)
    wb = openpyxl.load_workbook(path)
    ws = wb["ANNOTATION"]
    labels = []
    for row in ws.iter_rows(min_row=2, values_only=True):
        label = row[col_idx] if len(row) > col_idx else None
        labels.append(str(label).strip() if label else "")
    return labels

print("Loading annotator sheets...")
a1 = load_labels(BASE / "annotation_sheet_A1.xlsx")
a2 = load_labels(BASE / "annotation_sheet_A2.xlsx")

# Filter to only rows where both annotators provided a label
paired = [(l1, l2) for l1, l2 in zip(a1, a2)
          if l1 and l2 and l1 != "None" and l2 != "None"]

if not paired:
    print("No paired labels found. Make sure both annotators have filled in column E.")
    sys.exit(1)

y1 = [p[0] for p in paired]
y2 = [p[1] for p in paired]

kappa = cohen_kappa_score(y1, y2)
agreement = sum(l1 == l2 for l1, l2 in paired) / len(paired) * 100

print(f"\n{'='*60}")
print(f"INTER-ANNOTATOR AGREEMENT REPORT")
print(f"{'='*60}")
print(f"Messages with both labels:  {len(paired)}")
print(f"Simple agreement:           {agreement:.1f}%")
print(f"Cohen's Kappa:              {kappa:.4f}")
print(f"{'='*60}")

if kappa >= 0.80:
    print(f"RESULT: EXCELLENT agreement (kappa >= 0.80) ✓ — ready to publish")
elif kappa >= 0.61:
    print(f"RESULT: SUBSTANTIAL agreement (0.61-0.79) — review disagreements, discuss, re-label")
elif kappa >= 0.41:
    print(f"RESULT: MODERATE agreement (0.41-0.60) — significant discussion and revision needed")
else:
    print(f"RESULT: POOR agreement (<0.41) — guidelines need revision, repeat annotation")

print(f"\nTarget for publication: kappa >= 0.80")
print(f"{'='*60}")

# Category breakdown
labels_all = sorted(set(y1 + y2))
print(f"\nPER-CATEGORY BREAKDOWN:")
print(f"{'Category':<28} {'A1':>6} {'A2':>6} {'Agree':>8}")
print("-"*52)
for cat in labels_all:
    c1 = y1.count(cat)
    c2 = y2.count(cat)
    agree = sum(l1 == l2 == cat for l1, l2 in paired)
    print(f"{cat:<28} {c1:>6} {c2:>6} {agree:>8}")

# Disagreement analysis
print(f"\nDISAGREEMENTS (first 20):")
print(f"{'MSG':<8} {'Annotator 1':<28} {'Annotator 2':<28}")
print("-"*66)
count = 0
for i, (l1, l2) in enumerate(zip(y1, y2)):
    if l1 != l2:
        print(f"MSG{i+1:04d}  {l1:<28} {l2:<28}")
        count += 1
        if count >= 20:
            print("  ... (showing first 20 disagreements only)")
            break

print(f"\nSaved report. Kappa = {kappa:.4f}")

# Save CSV report
import csv
report_path = BASE / "kappa_report.csv"
with open(report_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["msg_id","annotator1","annotator2","agree"])
    for i, (l1, l2) in enumerate(zip(y1, y2)):
        w.writerow([f"MSG{i+1:04d}", l1, l2, l1==l2])
print(f"Full report saved → {report_path.name}")
