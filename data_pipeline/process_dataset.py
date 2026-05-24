#!/usr/bin/env python3
"""
Data Processing Pipeline for MFS Scam Research
Features:
  - Regex-based de-identification (phone numbers, NIDs, account numbers)
  - PII detection with Microsoft Presidio
  - Label distribution analysis
  - Feature extraction (textual + structural)
  - Dataset profiling for paper Table 1

Usage:
    python data_pipeline.py --input raw_messages.csv --output clean_dataset.csv
    python data_pipeline.py --profile clean_dataset.csv --report table1_stats.json

Requirements: pip install presidio-analyzer presidio-anonymizer pandas numpy
"""

import argparse
import csv
import json
import os
import re
import hashlib
from collections import Counter, defaultdict
from datetime import datetime

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("ERROR: Install pandas and numpy: pip install pandas numpy")
    raise

# Optional: Presidio for advanced PII detection
try:
    from presidio_analyzer import AnalyzerEngine
    from presidio_anonymizer import AnonymizerEngine
    PRESIDIO_AVAILABLE = True
except ImportError:
    PRESIDIO_AVAILABLE = False
    print("[!] Presidio not installed. Using regex-only de-identification.")
    print("    For full PII detection: pip install presidio-analyzer presidio-anonymizer")


# ============ DE-IDENTIFICATION RULES ============

# Bangladesh-specific patterns
DEID_PATTERNS = {
    # Mobile numbers: +8801XXXXXXXXX, 01XXXXXXXXX, 8801XXXXXXXXX
    'mobile_number': re.compile(
        r'\b(?:\+?8801|01|8801)[3-9]\d{8}\b'
    ),
    # Bangladesh NID (National ID): 10, 13, or 17 digits
    'nid_number': re.compile(
        r'\b\d{10}(?:\d{3})?(?:\d{4})?\b'
    ),
    # Bank account numbers (common lengths)
    'bank_account': re.compile(
        r'\b\d{9,16}\b'
    ),
    # Credit/debit card numbers
    'card_number': re.compile(
        r'\b(?:\d{4}[-\s]?){3,4}\d{1,4}\b'
    ),
    # Email addresses
    'email': re.compile(
        r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    ),
    # bKash/Nagad account numbers (11 digit mobile format)
    'mfs_account': re.compile(
        r'\b(?:\+?8801|01)[3-9]\d{8}\b'
    ),
    # PIN/OTP codes (standalone 4-6 digit numbers near keywords)
    'pin_otp': re.compile(
        r'(?i)(?:pin|otp|code|password)[\s:]*\d{4,6}'
    ),
    # Names (basic pattern - Presidio handles this better)
    'person_name': re.compile(
        r'\b(?:Mr|Mrs|Ms|Md|Mohammad|Muhammad|Md\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b'
    ),
}

# Replacement tokens
REPLACEMENT_TOKENS = {
    'mobile_number': '<PHONE>',
    'nid_number': '<NID>',
    'bank_account': '<ACCOUNT>',
    'card_number': '<CARD>',
    'email': '<EMAIL>',
    'mfs_account': '<MFS_ACCOUNT>',
    'pin_otp': '<PIN_OTP>',
    'person_name': '<NAME>',
}


def regex_deidentify(text):
    """De-identify text using regex patterns."""
    deid_log = []
    for pii_type, pattern in DEID_PATTERNS.items():
        matches = list(pattern.finditer(text))
        for match in matches:
            original = match.group()
            # Skip very short matches that might be false positives
            if len(original) < 4 and pii_type not in ['pin_otp']:
                continue
            replacement = REPLACEMENT_TOKENS.get(pii_type, f'<{pii_type.upper()}>')
            text = text.replace(original, replacement, 1)
            deid_log.append({
                'type': pii_type,
                'original': original,
                'replacement': replacement,
                'position': match.start()
            })
    return text, deid_log


def presidio_deidentify(text):
    """De-identify using Microsoft Presidio (more accurate)."""
    if not PRESIDIO_AVAILABLE:
        return regex_deidentify(text)

    analyzer = AnalyzerEngine()
    anonymizer = AnonymizerEngine()

    results = analyzer.analyze(text=text, language='en')
    anonymized = anonymizer.anonymize(text=text, analyzer_results=results)

    deid_log = []
    for result in results:
        deid_log.append({
            'type': result.entity_type,
            'original': text[result.start:result.end],
            'score': result.score,
            'position': result.start
        })

    return anonymized.text, deid_log


# ============ FEATURE EXTRACTION ============

# Bangla character detection
BANGLA_RANGE = range(0x0980, 0x09FF + 1)

def contains_bangla(text):
    return any(ord(c) in BANGLA_RANGE for c in text)

def bangla_ratio(text):
    bangla_chars = sum(1 for c in text if ord(c) in BANGLA_RANGE)
    total_alpha = sum(1 for c in text if c.isalpha())
    return bangla_chars / total_alpha if total_alpha > 0 else 0

# Urgency markers
URGENCY_WORDS = [
    'urgent', 'immediately', 'now', 'today', 'hurry', 'last chance',
    'expires', 'deadline', 'limited', 'act now', 'dont delay',
    'asap', 'quick', 'fast', 'instant', 'right now',
    # Bangla urgency
    'জরুরি', 'এখনি', 'আজই', 'দ্রুত', 'শেষ', 'সীমিত'
]

# Scam indicator words
SCAM_INDICATORS = [
    'free', 'won', 'winner', 'prize', 'lottery', 'bonus', 'cashback',
    'offer', 'gift', 'reward', 'claim', 'click here', 'verify',
    'suspended', 'blocked', 'unusual activity', 'security alert',
    'otp', 'pin', 'password', 'login', 'verify account',
    # Bangla scam terms
    'ফ্রি', 'পুরস্কার', 'জিতেছি', 'বোনাস', 'অফার', 'ভেরিফাই'
]

# Action verbs
ACTION_WORDS = [
    'send', 'click', 'call', 'reply', 'pay', 'transfer', 'verify',
    'confirm', 'update', 'download', 'install', 'register',
    'পাঠান', 'ক্লিক', 'কল', 'পেমেন্ট', 'ট্রান্সফার'
]


def extract_features(text):
    """Extract comprehensive features from a message."""
    text_lower = text.lower()
    words = text.split()

    features = {
        # Basic stats
        'char_count': len(text),
        'word_count': len(words),
        'sentence_count': len([s for s in re.split(r'[.!?।]', text) if s.strip()]),
        'avg_word_length': np.mean([len(w) for w in words]) if words else 0,

        # Language
        'contains_bangla': contains_bangla(text),
        'bangla_ratio': bangla_ratio(text),
        'contains_english': bool(re.search(r'[a-zA-Z]', text)),
        'is_code_mixed': contains_bangla(text) and bool(re.search(r'[a-zA-Z]', text)),

        # URL features
        'has_url': bool(re.search(r'http[s]?://|www\.', text_lower)),
        'url_count': len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)),
        'has_url_shortener': any(s in text_lower for s in ['bit.ly', 'tinyurl', 't.co', 'goo.gl']),

        # Phone number features
        'has_phone': bool(re.search(r'\b(?:\+?8801|01)[3-9]\d{8}\b', text)),
        'phone_count': len(re.findall(r'\b(?:\+?8801|01)[3-9]\d{8}\b', text)),

        # Content features
        'urgency_word_count': sum(1 for w in URGENCY_WORDS if w.lower() in text_lower),
        'has_urgency': any(w.lower() in text_lower for w in URGENCY_WORDS),

        'scam_indicator_count': sum(1 for w in SCAM_INDICATORS if w.lower() in text_lower),
        'has_scam_indicator': any(w.lower() in text_lower for w in SCAM_INDICATORS),

        'action_word_count': sum(1 for w in ACTION_WORDS if w.lower() in text_lower),
        'has_action': any(w.lower() in text_lower for w in ACTION_WORDS),

        # Punctuation/features
        'exclamation_count': text.count('!'),
        'question_count': text.count('?'),
        'all_caps_words': len([w for w in words if w.isupper() and len(w) > 1]),
        'digit_count': sum(c.isdigit() for c in text),
        'digit_ratio': sum(c.isdigit() for c in text) / len(text) if text else 0,

        # MFS-specific
        'mentions_bkash': 'bkash' in text_lower or 'বিকাশ' in text,
        'mentions_nagad': 'nagad' in text_lower or 'নগদ' in text,
        'mentions_rocket': 'rocket' in text_lower or 'রকেট' in text,
        'mentions_dbbl': 'dbbl' in text_lower,
        'mentions_otp': 'otp' in text_lower,
        'mentions_pin': 'pin' in text_lower,

        # Structural
        'has_spelling_error': False,  # Would need spell checker
        'readability_score': 0,  # Would need textstat
    }

    return features


# ============ DATASET PROFILING ============

def profile_dataset(df, label_col='label', text_col='message', category_col='category'):
    """Generate comprehensive dataset profile for paper Table 1."""
    profile = {
        'generated_at': datetime.now().isoformat(),
        'total_samples': len(df),
        'columns': list(df.columns),

        # Label distribution
        'label_distribution': df[label_col].value_counts().to_dict() if label_col in df.columns else {},
        'label_percentages': (df[label_col].value_counts(normalize=True) * 100).round(2).to_dict() if label_col in df.columns else {},

        # Category distribution
        'category_distribution': df[category_col].value_counts().to_dict() if category_col in df.columns else {},

        # Language analysis
        'language_stats': {
            'contains_bangla': 0,
            'contains_english': 0,
            'code_mixed': 0,
            'bangla_only': 0,
            'english_only': 0,
        },

        # Text statistics
        'text_stats': {
            'avg_message_length': 0,
            'median_message_length': 0,
            'min_message_length': 0,
            'max_message_length': 0,
        },

        # Feature distributions
        'feature_means': {},
        'feature_by_label': {},
    }

    # Language stats
    if text_col in df.columns:
        texts = df[text_col].astype(str)
        profile['language_stats']['contains_bangla'] = int(texts.apply(contains_bangla).sum())
        profile['language_stats']['contains_english'] = int(texts.apply(lambda t: bool(re.search(r'[a-zA-Z]', t))).sum())

        lengths = texts.apply(len)
        profile['text_stats'] = {
            'avg_message_length': round(float(lengths.mean()), 2),
            'median_message_length': round(float(lengths.median()), 2),
            'min_message_length': int(lengths.min()),
            'max_message_length': int(lengths.max()),
            'std_message_length': round(float(lengths.std()), 2),
        }

        # Compute language breakdown
        for text in texts:
            has_bn = contains_bangla(text)
            has_en = bool(re.search(r'[a-zA-Z]', text))
            if has_bn and has_en:
                profile['language_stats']['code_mixed'] += 1
            elif has_bn:
                profile['language_stats']['bangla_only'] += 1
            elif has_en:
                profile['language_stats']['english_only'] += 1

    # Feature extraction and analysis
    if text_col in df.columns:
        print("[+] Extracting features from all messages...")
        all_features = []
        for text in df[text_col].astype(str):
            features = extract_features(text)
            all_features.append(features)

        feature_df = pd.DataFrame(all_features)

        # Overall feature means
        numeric_cols = feature_df.select_dtypes(include=[np.number]).columns
        profile['feature_means'] = feature_df[numeric_cols].mean().round(4).to_dict()

        # Feature means by label
        if label_col in df.columns:
            feature_df[label_col] = df[label_col].values
            for label in df[label_col].unique():
                subset = feature_df[feature_df[label_col] == label]
                profile['feature_by_label'][str(label)] = subset[numeric_cols].mean().round(4).to_dict()

    return profile


def generate_table1(profile, output_path):
    """Generate formatted Table 1 for paper."""
    table1 = {
        'table_title': 'Dataset Profile: Financial Scams Detection Dataset',
        'dataset_size': profile['total_samples'],
        'label_distribution': profile['label_distribution'],
        'language_composition': profile['language_stats'],
        'message_length': profile['text_stats'],
        'key_features': {
            k: v for k, v in profile['feature_means'].items()
            if k in ['has_url', 'has_phone', 'has_urgency', 'has_scam_indicator',
                     'mentions_bkash', 'mentions_nagad', 'mentions_otp', 'is_code_mixed']
        }
    }

    with open(output_path, 'w') as f:
        json.dump(table1, f, indent=2)

    print("\n" + "="*60)
    print("TABLE 1: DATASET PROFILE")
    print("="*60)
    print(f"Dataset Size:          {table1['dataset_size']} messages")
    print(f"Label Distribution:    {table1['label_distribution']}")
    print(f"Language Composition:  {table1['language_composition']}")
    print(f"Message Length:        {table1['message_length']}")
    print(f"Key Features:          {table1['key_features']}")
    print("="*60)

    return table1


# ============ MAIN PIPELINE ============

def process_pipeline(input_csv, output_csv, profile_output=None, deidentify=True):
    """Run full processing pipeline."""
    print(f"[+] Loading data from: {input_csv}")
    df = pd.read_csv(input_csv)
    print(f"    Loaded {len(df)} records")

    # Auto-detect columns
    text_col = None
    label_col = None
    for col in df.columns:
        col_lower = col.lower()
        if any(k in col_lower for k in ['message', 'text', 'sms', 'content', 'body']):
            text_col = col
        if any(k in col_lower for k in ['label', 'class', 'category', 'type', 'ham', 'spam', 'scam']):
            label_col = col

    if text_col:
        print(f"    Detected text column: '{text_col}'")
    else:
        text_col = df.columns[0]
        print(f"    Using first column as text: '{text_col}'")

    if label_col:
        print(f"    Detected label column: '{label_col}'")
    else:
        label_col = df.columns[1] if len(df.columns) > 1 else None
        print(f"    Using column as label: '{label_col}'")

    # De-identification
    if deidentify:
        print("[+] Running de-identification...")
        deid_count = 0
        deident_logs = []

        for idx, text in enumerate(df[text_col].astype(str)):
            if PRESIDIO_AVAILABLE:
                clean_text, log = presidio_deidentify(text)
            else:
                clean_text, log = regex_deidentify(text)

            if log:
                deid_count += 1
                deident_logs.extend(log)

            df.at[idx, text_col] = clean_text

        print(f"    De-identified {deid_count}/{len(df)} messages")
        print(f"    PII instances found: {len(deident_logs)}")
        if deident_logs:
            pii_types = Counter(entry['type'] for entry in deident_logs)
            print(f"    PII type breakdown: {dict(pii_types)}")

    # Feature extraction
    print("[+] Extracting features...")
    all_features = []
    for text in df[text_col].astype(str):
        features = extract_features(text)
        all_features.append(features)

    feature_df = pd.DataFrame(all_features)
    feature_df.columns = [f'feat_{c}' for c in feature_df.columns]

    # Merge features with original data
    df_output = pd.concat([df.reset_index(drop=True), feature_df], axis=1)

    # Save processed data
    df_output.to_csv(output_csv, index=False)
    print(f"[+] Saved processed data: {output_csv}")

    # Profile
    category_col = None
    for col in df.columns:
        if 'category' in col.lower() or 'type' in col.lower():
            category_col = col
            break

    profile = profile_dataset(df, label_col=label_col, text_col=text_col, category_col=category_col)

    if profile_output:
        generate_table1(profile, profile_output)

    return df_output, profile


def main():
    parser = argparse.ArgumentParser(description="MFS Scam Data Processing Pipeline")
    parser.add_argument("--input", required=True, help="Input CSV file")
    parser.add_argument("--output", required=True, help="Output CSV file")
    parser.add_argument("--profile", help="Output profile JSON (Table 1 stats)")
    parser.add_argument("--no-deidentify", action="store_true", help="Skip de-identification")
    parser.add_argument("--features-only", action="store_true", help="Only extract features")

    args = parser.parse_args()

    process_pipeline(
        args.input,
        args.output,
        profile_output=args.profile,
        deidentify=not args.no_deidentify
    )

    print("\n[*] Pipeline complete!")


if __name__ == "__main__":
    main()
