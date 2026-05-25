"""
BanglaBERT Training Pipeline v2
=================================
MFS Scam Ecosystem Study — LSU, 2025
Author: Md. Saidur Rahman

Improvements over v1:
  1. Trains on full merged corpus (3,000+ msgs), tests on gold 600
  2. Class-weighted cross-entropy loss (handles imbalance)
  3. Binary classifier (scam vs ham) — headline result
  4. 7-class classifier with weighted loss — detailed result

Run build_training_data.py first to generate:
  - training_corpus.csv
  - gold_test.csv

Usage:
  python build_training_data.py
  python train_v2.py
"""

import os, random, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torch.optim import AdamW
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification,
    get_linear_schedule_with_warmup
)
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (
    classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, accuracy_score
)
from sklearn.utils.class_weight import compute_class_weight

warnings.filterwarnings("ignore")

# ── Config ────────────────────────────────────────────────────────────────────

TRAIN_CSV     = "training_corpus.csv"
TEST_CSV      = "gold_test.csv"
OUTPUT_DIR    = Path("model_outputs_v2")
SEED          = 42
MAX_LEN       = 128
BATCH_SIZE    = 16
EPOCHS        = 10
LR            = 2e-5
WEIGHT_DECAY  = 0.01
WARMUP_RATIO  = 0.1
PATIENCE      = 3

BANGLABERT_MODEL = "csebuetnlp/banglabert"

CATEGORIES = [
    "L0_Ham",
    "S1_AccountCompromise",
    "S2_FakePromo",
    "S3_LotteryPrize",
    "S4_LoanJob",
    "S5_Impersonation",
    "S6_PhishingLink",
]

def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(SEED)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "results").mkdir(exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"\n{'='*60}")
print(f"  BanglaBERT MFS Scam Classifier v2")
print(f"  Device: {device}")
print(f"{'='*60}\n")

# ── Load data ─────────────────────────────────────────────────────────────────

print("[1/7] Loading datasets...")
train_df = pd.read_csv(TRAIN_CSV, encoding="utf-8")
test_df  = pd.read_csv(TEST_CSV,  encoding="utf-8")

# Clean
train_df = train_df[train_df["label"].isin(CATEGORIES)].dropna(subset=["text","label"])
test_df  = test_df[test_df["label"].isin(CATEGORIES)].dropna(subset=["text","label"])
train_df["text"] = train_df["text"].astype(str)
test_df["text"]  = test_df["text"].astype(str)

print(f"  Training corpus : {len(train_df)} messages")
print(f"  Gold test set   : {len(test_df)} messages")

print("\n  Training label distribution:")
from collections import Counter
dist = Counter(train_df["label"])
for cat in CATEGORIES:
    n = dist.get(cat, 0)
    print(f"    {cat:<28} {n:>5}  ({100*n/len(train_df):.1f}%)")

# Encode 7-class labels
le7 = LabelEncoder()
le7.fit(CATEGORIES)
train_df["label_id"] = le7.transform(train_df["label"])
test_df["label_id"]  = le7.transform(test_df["label"])

# Binary labels (0=Ham, 1=Scam)
train_df["binary_id"] = (train_df["label"] != "L0_Ham").astype(int)
test_df["binary_id"]  = (test_df["label"]  != "L0_Ham").astype(int)

# Dev split from training data (10%)
train_core, dev_df = train_test_split(
    train_df, test_size=0.10, random_state=SEED, stratify=train_df["label_id"]
)
print(f"\n  Train core: {len(train_core)}  Dev: {len(dev_df)}  Test (gold): {len(test_df)}")

# ── Compute class weights ─────────────────────────────────────────────────────

print("\n[2/7] Computing class weights...")

# 7-class weights
cw7 = compute_class_weight("balanced",
                            classes=np.array(range(len(CATEGORIES))),
                            y=train_core["label_id"].values)
class_weights_7 = torch.tensor(cw7, dtype=torch.float).to(device)
print("  7-class weights:")
for cat, w in zip(CATEGORIES, cw7):
    print(f"    {cat:<28} weight={w:.3f}")

# Binary weights
cw_bin = compute_class_weight("balanced",
                               classes=np.array([0, 1]),
                               y=train_core["binary_id"].values)
class_weights_bin = torch.tensor(cw_bin, dtype=torch.float).to(device)
print(f"\n  Binary weights: Ham={cw_bin[0]:.3f}  Scam={cw_bin[1]:.3f}")

# ── Dataset class ─────────────────────────────────────────────────────────────

class ScamDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_len=MAX_LEN):
        self.texts  = list(texts)
        self.labels = list(labels)
        self.tok    = tokenizer
        self.max_len = max_len

    def __len__(self): return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tok(self.texts[idx], max_length=self.max_len,
                       padding="max_length", truncation=True, return_tensors="pt")
        return {
            "input_ids":      enc["input_ids"].squeeze(),
            "attention_mask": enc["attention_mask"].squeeze(),
            "labels":         torch.tensor(self.labels[idx], dtype=torch.long)
        }

# ── Training helpers ──────────────────────────────────────────────────────────

def train_epoch(model, loader, optimizer, scheduler, criterion):
    model.train()
    total_loss = 0
    for batch in loader:
        optimizer.zero_grad()
        out = model(input_ids      = batch["input_ids"].to(device),
                    attention_mask = batch["attention_mask"].to(device))
        loss = criterion(out.logits, batch["labels"].to(device))
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        total_loss += loss.item()
    return total_loss / len(loader)

def evaluate(model, loader, criterion):
    model.eval()
    all_preds, all_labels, total_loss = [], [], 0
    with torch.no_grad():
        for batch in loader:
            out = model(input_ids      = batch["input_ids"].to(device),
                        attention_mask = batch["attention_mask"].to(device))
            loss = criterion(out.logits, batch["labels"].to(device))
            total_loss += loss.item()
            preds = torch.argmax(out.logits, dim=1).cpu().numpy()
            all_preds.extend(preds)
            all_labels.extend(batch["labels"].numpy())
    macro_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
    return total_loss / len(loader), macro_f1, all_preds, all_labels

def fine_tune(model_name, num_labels, train_texts, train_labels,
              dev_texts, dev_labels, class_weights, save_dir, tag):
    print(f"\n{'─'*60}")
    print(f"[Training] {tag}  —  {num_labels} classes")
    print(f"{'─'*60}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=num_labels).to(device)

    criterion = nn.CrossEntropyLoss(weight=class_weights)

    train_ds = ScamDataset(train_texts, train_labels, tokenizer)
    dev_ds   = ScamDataset(dev_texts,   dev_labels,   tokenizer)
    train_loader = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True)
    dev_loader   = DataLoader(dev_ds,   batch_size=BATCH_SIZE)

    total_steps  = len(train_loader) * EPOCHS
    warmup_steps = int(total_steps * WARMUP_RATIO)
    optimizer    = AdamW(model.parameters(), lr=LR, weight_decay=WEIGHT_DECAY)
    scheduler    = get_linear_schedule_with_warmup(optimizer, warmup_steps, total_steps)

    best_f1, patience_ctr, best_state = 0.0, 0, None

    for epoch in range(1, EPOCHS + 1):
        tr_loss = train_epoch(model, train_loader, optimizer, scheduler, criterion)
        dv_loss, dv_f1, _, _ = evaluate(model, dev_loader, criterion)
        print(f"  Epoch {epoch:>2}/{EPOCHS}  "
              f"train_loss={tr_loss:.4f}  dev_loss={dv_loss:.4f}  "
              f"dev_macro_F1={dv_f1:.4f}", end="")

        if dv_f1 > best_f1:
            best_f1, patience_ctr = dv_f1, 0
            best_state = {k: v.cpu().clone() for k, v in model.state_dict().items()}
            print("  ← best")
        else:
            patience_ctr += 1
            print(f"  (patience {patience_ctr}/{PATIENCE})")
            if patience_ctr >= PATIENCE:
                print(f"  Early stopping at epoch {epoch}")
                break

    model.load_state_dict(best_state)
    model.to(device)
    path = OUTPUT_DIR / save_dir
    model.save_pretrained(path)
    tokenizer.save_pretrained(path)
    print(f"  Model saved → {path}")
    return model, tokenizer, criterion

def plot_cm(labels, preds, cat_names, title, fname):
    cm = confusion_matrix(labels, preds)
    fig, ax = plt.subplots(figsize=(max(6, len(cat_names)), max(5, len(cat_names)-1)))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
                xticklabels=cat_names, yticklabels=cat_names, ax=ax)
    ax.set_xlabel("Predicted"); ax.set_ylabel("True")
    ax.set_title(title, fontweight="bold")
    plt.tight_layout()
    p = OUTPUT_DIR / "results" / fname
    plt.savefig(p, dpi=150); plt.close()
    print(f"  Confusion matrix saved → {p}")

# ── [3/7] TF-IDF baseline (7-class) ──────────────────────────────────────────

print("\n[3/7] TF-IDF + LR baseline (7-class, weighted)...")
tfidf = TfidfVectorizer(analyzer="char_wb", ngram_range=(2,4),
                        max_features=50000, sublinear_tf=True)
X_tr = tfidf.fit_transform(train_core["text"])
X_te = tfidf.transform(test_df["text"])

sample_w = compute_class_weight("balanced",
                                 classes=np.unique(train_core["label_id"]),
                                 y=train_core["label_id"].values)
sw_dict = {i: w for i, w in enumerate(sample_w)}
sw_train = np.array([sw_dict[i] for i in train_core["label_id"]])

lr7 = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs", random_state=SEED)
lr7.fit(X_tr, train_core["label_id"], sample_weight=sw_train)
lr7_preds = lr7.predict(X_te)
lr7_f1 = f1_score(test_df["label_id"], lr7_preds, average="macro", zero_division=0)
lr7_w_f1 = f1_score(test_df["label_id"], lr7_preds, average="weighted", zero_division=0)
print(f"  TF-IDF 7-class  macro-F1={lr7_f1:.4f}  weighted-F1={lr7_w_f1:.4f}")
lr7_report = classification_report(test_df["label_id"], lr7_preds,
                                    target_names=CATEGORIES, zero_division=0)
print(lr7_report)

# ── [4/7] TF-IDF binary baseline ─────────────────────────────────────────────

print("\n[4/7] TF-IDF + LR binary (scam vs ham)...")
lr_bin = LogisticRegression(max_iter=1000, C=1.0, solver="lbfgs", random_state=SEED,
                             class_weight="balanced")
lr_bin.fit(X_tr, train_core["binary_id"])
lr_bin_preds = lr_bin.predict(X_te)
lr_bin_f1 = f1_score(test_df["binary_id"], lr_bin_preds, average="macro", zero_division=0)
lr_bin_acc = accuracy_score(test_df["binary_id"], lr_bin_preds)
print(f"  TF-IDF binary  macro-F1={lr_bin_f1:.4f}  accuracy={lr_bin_acc:.4f}")
lr_bin_report = classification_report(test_df["binary_id"], lr_bin_preds,
                                       target_names=["Ham","Scam"], zero_division=0)
print(lr_bin_report)

# ── [5/7] BanglaBERT 7-class (weighted) ──────────────────────────────────────

print("\n[5/7] Fine-tuning BanglaBERT 7-class (weighted loss)...")
bb7_model, bb7_tok, bb7_crit = fine_tune(
    BANGLABERT_MODEL, len(CATEGORIES),
    train_core["text"], train_core["label_id"],
    dev_df["text"],     dev_df["label_id"],
    class_weights_7, "banglabert_7class", "BanglaBERT 7-class"
)

# Evaluate on gold test
test_ds7 = ScamDataset(test_df["text"], test_df["label_id"], bb7_tok)
test_loader7 = DataLoader(test_ds7, batch_size=BATCH_SIZE)
_, bb7_mf1, bb7_preds, bb7_labels = evaluate(bb7_model, test_loader7, bb7_crit)
bb7_wf1 = f1_score(bb7_labels, bb7_preds, average="weighted", zero_division=0)
print(f"\n  BanglaBERT 7-class  macro-F1={bb7_mf1:.4f}  weighted-F1={bb7_wf1:.4f}")
bb7_report = classification_report(bb7_labels, bb7_preds,
                                    target_names=CATEGORIES, zero_division=0)
print(bb7_report)
plot_cm(bb7_labels, bb7_preds,
        ["Ham","S1","S2","S3","S4","S5","S6"],
        "BanglaBERT 7-class (weighted)", "cm_bb_7class.png")

# ── [6/7] BanglaBERT binary ──────────────────────────────────────────────────

print("\n[6/7] Fine-tuning BanglaBERT binary (scam vs ham)...")
bb_bin_model, bb_bin_tok, bb_bin_crit = fine_tune(
    BANGLABERT_MODEL, 2,
    train_core["text"], train_core["binary_id"],
    dev_df["text"],     dev_df["binary_id"],
    class_weights_bin, "banglabert_binary", "BanglaBERT Binary"
)

test_ds_bin = ScamDataset(test_df["text"], test_df["binary_id"], bb_bin_tok)
test_loader_bin = DataLoader(test_ds_bin, batch_size=BATCH_SIZE)
_, bb_bin_mf1, bb_bin_preds, bb_bin_labels = evaluate(
    bb_bin_model, test_loader_bin, bb_bin_crit)
bb_bin_acc = accuracy_score(bb_bin_labels, bb_bin_preds)
bb_bin_wf1 = f1_score(bb_bin_labels, bb_bin_preds, average="weighted", zero_division=0)
print(f"\n  BanglaBERT binary  macro-F1={bb_bin_mf1:.4f}  "
      f"weighted-F1={bb_bin_wf1:.4f}  accuracy={bb_bin_acc:.4f}")
bb_bin_report = classification_report(bb_bin_labels, bb_bin_preds,
                                       target_names=["Ham","Scam"], zero_division=0)
print(bb_bin_report)
plot_cm(bb_bin_labels, bb_bin_preds, ["Ham","Scam"],
        "BanglaBERT Binary (scam vs ham)", "cm_bb_binary.png")

# ── [7/7] Summary report ─────────────────────────────────────────────────────

print("\n[7/7] Writing summary report...")

rpt = OUTPUT_DIR / "results" / "classification_report_v2.txt"
with open(rpt, "w", encoding="utf-8") as f:
    def w(s=""): f.write(s + "\n"); print(s)
    w("="*65)
    w("  MFS SCAM CLASSIFIER v2 — EVALUATION REPORT")
    w("  LSU 2025 | Md. Saidur Rahman")
    w("="*65)
    w(f"\n  Training corpus  : {len(train_core)} messages")
    w(f"  Dev set          : {len(dev_df)} messages")
    w(f"  Gold test set    : {len(test_df)} messages (annotated, never trained on)")
    w(f"  Device           : {device}")
    w()
    w("  ── BINARY CLASSIFICATION (Scam vs Ham) ──────────────────")
    w(f"  TF-IDF + LR  macro-F1={lr_bin_f1:.4f}  acc={lr_bin_acc:.4f}")
    w(f"  BanglaBERT   macro-F1={bb_bin_mf1:.4f}  acc={bb_bin_acc:.4f}")
    w()
    w("  BanglaBERT Binary Classification Report:")
    w(bb_bin_report)
    w()
    w("  ── 7-CLASS CLASSIFICATION (weighted loss) ───────────────")
    w(f"  TF-IDF + LR  macro-F1={lr7_f1:.4f}  weighted-F1={lr7_w_f1:.4f}")
    w(f"  BanglaBERT   macro-F1={bb7_mf1:.4f}  weighted-F1={bb7_wf1:.4f}")
    w()
    w("  BanglaBERT 7-class Classification Report:")
    w(bb7_report)
    w("="*65)

print(f"\n  Full report → {rpt}")
print(f"\n{'='*60}")
print(f"  TRAINING COMPLETE (v2)")
print(f"  BanglaBERT binary   macro-F1 : {bb_bin_mf1:.4f}")
print(f"  BanglaBERT 7-class  macro-F1 : {bb7_mf1:.4f}")
print(f"{'='*60}\n")
