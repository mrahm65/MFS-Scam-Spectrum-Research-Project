"""
Training Dataset Builder
=========================
MFS Scam Ecosystem Study — LSU, 2025
Author: Md. Saidur Rahman

Merges all available labelled data into a single training corpus:
  - stream_a_datasets/clean_dataset_1.csv  (523 msgs — Financial Scams)
  - stream_a_datasets/clean_dataset_2.csv  (2,772 msgs — BanglaBarta)

Maps original labels → 7-category taxonomy using keyword rules.
Outputs:
  - training_corpus.csv   (all merged data, for model training)
  - gold_test.csv         (600 gold annotations, NEVER used for training)

Usage:
  python build_training_data.py
"""

import pandas as pd
import re
from pathlib import Path
from collections import Counter

# ── Paths ─────────────────────────────────────────────────────────────────────
DS1_PATH  = Path("stream_a_datasets/clean_dataset_1.csv")
DS2_PATH  = Path("stream_a_datasets/clean_dataset_2.csv")
GOLD_PATH = Path("kappa_adjudication_GOLD.csv")
OUT_TRAIN = Path("training_corpus.csv")
OUT_TEST  = Path("gold_test.csv")

# ── 7-class taxonomy ─────────────────────────────────────────────────────────
CATEGORIES = [
    "L0_Ham",
    "S1_AccountCompromise",
    "S2_FakePromo",
    "S3_LotteryPrize",
    "S4_LoanJob",
    "S5_Impersonation",
    "S6_PhishingLink",
]

# ── Keyword rules for sub-categorising "scam" messages ───────────────────────
# Priority order matches taxonomy: S6 > S5 > S1 > S2 > S3 > S4

KEYWORD_RULES = [
    # S6_PhishingLink — URL / app download present
    ("S6_PhishingLink",      r"http|www\.|\.com|\.net|\.org|apk|ডাউনলোড|লিংক|link|click|<URL>"),
    # S5_Impersonation — pretending to be bKash/Nagad/bank official
    ("S5_Impersonation",     r"bkash\s*(official|support|helpline|agent)|nagad\s*(official|support)|"
                             r"ব্যাংক.*অফিসার|কর্মকর্তা|government|সরকার"),
    # S1_AccountCompromise — OTP, PIN, password, account block
    ("S1_AccountCompromise", r"otp|ওটিপি|pin|পিন|password|পাসওয়ার্ড|block|ব্লক|verify|ভেরিফাই|"
                             r"account.*suspend|একাউন্ট.*বন্ধ|login|লগইন|credential"),
    # S2_FakePromo — cashback, bonus, offer, discount
    ("S2_FakePromo",         r"cashback|ক্যাশব্যাক|bonus|বোনাস|offer|অফার|discount|ছাড়|"
                             r"free|ফ্রি|promo|প্রমো|reward|রিওয়ার্ড"),
    # S3_LotteryPrize — prize, lottery, winner, gift
    ("S3_LotteryPrize",      r"prize|পুরস্কার|lottery|লটারি|winner|বিজয়ী|lucky|ভাগ্যবান|"
                             r"gift|উপহার|win|জিতেছেন|selected|নির্বাচিত"),
    # S4_LoanJob — loan, job, earn, income, investment
    ("S4_LoanJob",           r"loan|লোন|ঋণ|job|চাকরি|earn|আয়|income|ইনকাম|invest|"
                             r"work.from.home|ঘরে বসে|daily.*taka|টাকা.*দিন"),
]

def keyword_classify(text: str) -> str:
    """Apply keyword rules in priority order. Returns category label."""
    if not isinstance(text, str):
        return "L0_Ham"
    text_lower = text.lower()
    for label, pattern in KEYWORD_RULES:
        if re.search(pattern, text_lower, re.IGNORECASE):
            return label
    return "L0_Ham"

# ── Load Dataset 1 (Financial Scams — Ahmed & Islam 2024) ────────────────────
print("[1/4] Loading Dataset 1 (Financial Scams)...")

rows1 = []
if DS1_PATH.exists():
    df1 = pd.read_csv(DS1_PATH, encoding="utf-8")
    print(f"      Columns: {list(df1.columns)}")
    print(f"      Shape: {df1.shape}")

    # Find text and label columns
    text_col = next((c for c in df1.columns if "text" in c.lower() or
                     "message" in c.lower() or "sms" in c.lower()), df1.columns[0])
    label_col = next((c for c in df1.columns if "label" in c.lower() or
                      "class" in c.lower() or "category" in c.lower()), None)

    print(f"      Text col: '{text_col}'  Label col: '{label_col}'")

    for _, row in df1.iterrows():
        text = str(row[text_col]).strip() if text_col else ""
        if not text or text == "nan":
            continue

        orig_label = str(row[label_col]).strip().lower() if label_col else "scam"

        if orig_label in ("ham", "normal", "legitimate", "0"):
            tax_label = "L0_Ham"
        else:
            # "scam" → sub-categorise by keyword
            tax_label = keyword_classify(text)

        rows1.append({"text": text, "label": tax_label, "source": "mendeley_financial"})

    print(f"      Loaded {len(rows1)} messages from Dataset 1")
else:
    print(f"      ⚠  Not found: {DS1_PATH}")

# ── Load Dataset 2 (BanglaBarta SMS) ─────────────────────────────────────────
print("\n[2/4] Loading Dataset 2 (BanglaBarta)...")

rows2 = []
if DS2_PATH.exists():
    df2 = pd.read_csv(DS2_PATH, encoding="utf-8")
    print(f"      Columns: {list(df2.columns)}")
    print(f"      Shape: {df2.shape}")

    text_col2  = next((c for c in df2.columns if "text" in c.lower() or
                       "message" in c.lower() or "sms" in c.lower()), df2.columns[0])
    label_col2 = next((c for c in df2.columns if "label" in c.lower() or
                       "class" in c.lower() or "category" in c.lower()), None)

    print(f"      Text col: '{text_col2}'  Label col: '{label_col2}'")

    for _, row in df2.iterrows():
        text = str(row[text_col2]).strip() if text_col2 else ""
        if not text or text == "nan":
            continue

        orig_label = str(row[label_col2]).strip().lower() if label_col2 else "smish"

        # BanglaBarta label mapping
        if orig_label in ("ham", "normal", "legitimate", "0", "non-spam"):
            tax_label = "L0_Ham"
        elif orig_label in ("promo", "promotional", "advertisement"):
            tax_label = "S2_FakePromo"
        elif orig_label in ("smish", "smishing", "spam", "fraud", "scam", "1"):
            tax_label = keyword_classify(text)
        else:
            tax_label = keyword_classify(text)

        rows2.append({"text": text, "label": tax_label, "source": "banglabarta"})

    print(f"      Loaded {len(rows2)} messages from Dataset 2")
else:
    print(f"      ⚠  Not found: {DS2_PATH}")

# ── Load gold test set (600 gold-annotated — DO NOT use for training) ─────────
print("\n[3/4] Loading gold test set (600 annotated messages)...")

gold_ids = set()
gold_rows = []
if GOLD_PATH.exists():
    dfg = pd.read_csv(GOLD_PATH, encoding="utf-8")
    dfg = dfg[dfg["GOLD_LABEL"].notna() & (dfg["GOLD_LABEL"] != "")]
    for _, row in dfg.iterrows():
        gold_rows.append({
            "text":   str(row["TEXT"]).strip(),
            "label":  str(row["GOLD_LABEL"]).strip(),
            "source": "gold_annotated"
        })
        gold_ids.add(str(row["TEXT"]).strip()[:80])  # dedup key

    gold_df = pd.DataFrame(gold_rows)
    gold_df.to_csv(OUT_TEST, index=False, encoding="utf-8")
    print(f"      Gold test set: {len(gold_rows)} messages → saved to {OUT_TEST}")
else:
    print(f"      ⚠  Not found: {GOLD_PATH}")

# ── Build combined training corpus ────────────────────────────────────────────
print("\n[4/4] Building combined training corpus...")

all_rows = rows1 + rows2
train_df = pd.DataFrame(all_rows)

# Remove exact duplicates
train_df = train_df.drop_duplicates(subset=["text"]).reset_index(drop=True)

# Remove any messages that appear in the gold test set
def in_gold(text):
    return str(text).strip()[:80] in gold_ids

before = len(train_df)
train_df = train_df[~train_df["text"].apply(in_gold)].reset_index(drop=True)
after = len(train_df)
removed = before - after
if removed > 0:
    print(f"      Removed {removed} messages that overlap with gold test set")

# Remove empty texts
train_df = train_df[train_df["text"].str.len() > 5].reset_index(drop=True)

train_df.to_csv(OUT_TRAIN, index=False, encoding="utf-8")

print(f"\n{'='*55}")
print(f"  TRAINING CORPUS BUILT")
print(f"{'='*55}")
print(f"  Total training messages : {len(train_df)}")
print(f"  Gold test messages      : {len(gold_rows)}")
print(f"\n  Training label distribution:")
dist = Counter(train_df["label"])
total = len(train_df)
for cat in CATEGORIES:
    n = dist.get(cat, 0)
    bar = "█" * (n // 20)
    print(f"    {cat:<28} {n:>5}  ({100*n/total:.1f}%)  {bar}")

print(f"\n  Files saved:")
print(f"    {OUT_TRAIN}  ← use this for training")
print(f"    {OUT_TEST}   ← use this for evaluation ONLY")
print(f"{'='*55}")
