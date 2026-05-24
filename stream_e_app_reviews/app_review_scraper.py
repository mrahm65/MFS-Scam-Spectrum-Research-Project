#!/usr/bin/env python3
"""
Stream E: Google Play App Review Scraper for MFS Fraud Analysis
Target Apps: bKash, Nagad, Rocket, Upay
Filters reviews for fraud-related keywords in English and Bangla

Usage:
    python app_review_scraper.py --app com.bKash.customerapp --count 5000
    python app_review_scraper.py --all --count 10000 --output reviews.json

Requirements: pip install google-play-scraper pandas
"""

import argparse
import json
import csv
import re
import os
from datetime import datetime
from collections import Counter

# google-play-scraper import
try:
    from google_play_scraper import reviews, Sort
except ImportError:
    print("ERROR: Install google-play-scraper: pip install google-play-scraper")
    raise

# ============ CONFIGURATION ============

# Target MFS apps with their Google Play package names
MFS_APPS = {
    "bkash": {
        "package": "com.bKash.customerapp",
        "display_name": "bKash",
        "category": "MFS"
    },
    "nagad": {
        "package": "com.konasl.nagad",
        "display_name": "Nagad",
        "category": "MFS"
    },
    "rocket": {
        "package": "com.dbbl.mbs.apps.main",
        "display_name": "Rocket (DBBL)",
        "category": "MFS"
    },
    "upay": {
        "package": "com.upay",
        "display_name": "Upay",
        "category": "MFS"
    },
    "surecash": {
        "package": "com.progotisystems.android.surecash",
        "display_name": "SureCash",
        "category": "MFS"
    }
}

# Fraud-related keywords (English + Bangla/romanized)
FRAUD_KEYWORDS_EN = [
    'fraud', 'scam', 'cheat', 'steal', 'stolen', 'hack', 'hacked',
    'otp', 'pin', 'password', 'phish', 'fake', 'trap', 'deceive',
    'money gone', 'lost money', 'unauthorized', 'transaction failed',
    'account hacked', 'money deducted', 'balance gone',
    'fake call', 'fraud call', 'cheated', 'robbed',
    'suspicious', 'unauthorized transaction', 'refund not received',
    'customer care fraud', 'fake customer care'
]

FRAUD_KEYWORDS_BN = [
    'pratarona', 'প্রতারণা', 'ঠকিয়েছে', 'টাকা চলে গেছে',
    'ফেক', 'ভুয়া', 'ঝুঁকি', 'চুরি', 'হ্যাক',
    'একাউন্ট হ্যাক', 'টাকা কেটে নিয়েছে', 'ব্যালেন্স শেষ',
    'প্রতারক', 'ঠগ', 'মিথ্যা', 'জালিয়াতি'
]

ALL_FRAUD_KEYWORDS = FRAUD_KEYWORDS_EN + FRAUD_KEYWORDS_BN

# Scam category classifier patterns (regex-based pre-labeling)
SCAM_PATTERNS = {
    "otp_fraud": re.compile(r'otp|OTP|পিন|pin', re.IGNORECASE),
    "fake_customer_care": re.compile(r'customer care|helpline|সাপোর্ট|support', re.IGNORECASE),
    "account_hack": re.compile(r'hack|hacked|অ্যাকাউন্ট|account.*compromis|unauthorized', re.IGNORECASE),
    "money_loss": re.compile(r'stol.*money|lost.*money|money.*gone|টাকা.*চলে|টাকা.*কেটে|balance.*deduct', re.IGNORECASE),
    "phishing": re.compile(r'phish|link|url|click|fake.*website|ভুয়া.*লিঙ্ক', re.IGNORECASE),
    "fake_offer": re.compile(r'fake.*offer|bonus|cashback|free.*taka|লোটারি|lottery|পুরস্কার', re.IGNORECASE),
    "transaction_issue": re.compile(r'transaction.*fail|payment.*fail|send.*fail|টাকা.*যায়নি', re.IGNORECASE),
}


def categorize_review(text):
    """Pre-label review with scam category based on keyword patterns."""
    text_lower = (text or "").lower()
    categories = []
    for cat_name, pattern in SCAM_PATTERNS.items():
        if pattern.search(text_lower):
            categories.append(cat_name)
    return categories if categories else ["general_complaint"]


def contains_fraud_keyword(text):
    """Check if review contains any fraud-related keyword."""
    text_lower = (text or "").lower()
    return any(kw.lower() in text_lower for kw in ALL_FRAUD_KEYWORDS)


def scrape_reviews(package_name, app_name, count=5000, lang="en", country="us"):
    """Scrape reviews for a single app."""
    print(f"[+] Scraping {count} reviews for {app_name} ({package_name})...")

    all_reviews = []
    continuation_token = None
    batch_size = 150  # Max per request

    while len(all_reviews) < count:
        remaining = min(batch_size, count - len(all_reviews))
        try:
            result, continuation_token = reviews(
                package_name,
                lang=lang,
                country=country,
                sort=Sort.NEWEST,
                count=remaining,
                continuation_token=continuation_token
            )
        except Exception as e:
            print(f"    [!] Error scraping batch: {e}")
            break

        if not result:
            print(f"    [!] No more reviews available.")
            break

        for review in result:
            review_data = {
                "reviewId": review.get("reviewId", ""),
                "content": review.get("content", ""),
                "score": review.get("score", 0),
                "thumbsUpCount": review.get("thumbsUpCount", 0),
                "reviewCreatedVersion": review.get("reviewCreatedVersion", ""),
                "at": review.get("at", "").isoformat() if hasattr(review.get("at", ""), 'isoformat') else str(review.get("at", "")),
                "app_name": app_name,
                "package_name": package_name,
                "has_fraud_keyword": contains_fraud_keyword(review.get("content", "")),
                "scam_categories": categorize_review(review.get("content", "")),
                "scraped_at": datetime.now().isoformat()
            }
            all_reviews.append(review_data)

        print(f"    -> Collected {len(all_reviews)}/{count} reviews...")

        if continuation_token is None:
            break

    print(f"[+] Done: {len(all_reviews)} reviews collected for {app_name}")
    return all_reviews


def generate_statistics(reviews_list):
    """Generate profiling statistics from collected reviews."""
    fraud_reviews = [r for r in reviews_list if r["has_fraud_keyword"]]

    stats = {
        "total_reviews": len(reviews_list),
        "fraud_keyword_reviews": len(fraud_reviews),
        "fraud_percentage": round(len(fraud_reviews) / len(reviews_list) * 100, 2) if reviews_list else 0,
        "avg_rating_all": round(sum(r["score"] for r in reviews_list) / len(reviews_list), 2) if reviews_list else 0,
        "avg_rating_fraud": round(sum(r["score"] for r in fraud_reviews) / len(fraud_reviews), 2) if fraud_reviews else 0,
        "rating_distribution": dict(Counter(r["score"] for r in reviews_list)),
        "category_distribution": {},
        "app_distribution": dict(Counter(r["app_name"] for r in reviews_list)),
        "fraud_app_distribution": dict(Counter(r["app_name"] for r in fraud_reviews)),
        "top_thumbs_up": sorted(reviews_list, key=lambda x: x["thumbsUpCount"], reverse=True)[:10],
    }

    # Category distribution across fraud reviews
    all_cats = []
    for r in fraud_reviews:
        all_cats.extend(r["scam_categories"])
    stats["category_distribution"] = dict(Counter(all_cats))

    return stats


def save_outputs(reviews_list, output_dir, prefix="app_reviews"):
    """Save reviews in multiple formats."""
    os.makedirs(output_dir, exist_ok=True)

    # JSON (full data)
    json_path = os.path.join(output_dir, f"{prefix}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(reviews_list, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved JSON: {json_path} ({len(reviews_list)} records)")

    # CSV (flattened)
    csv_path = os.path.join(output_dir, f"{prefix}.csv")
    if reviews_list:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=reviews_list[0].keys())
            writer.writeheader()
            for r in reviews_list:
                row = r.copy()
                row["scam_categories"] = "|".join(row["scam_categories"])
                writer.writerow(row)
        print(f"[+] Saved CSV: {csv_path}")

    # Fraud-only subset
    fraud_reviews = [r for r in reviews_list if r["has_fraud_keyword"]]
    fraud_json_path = os.path.join(output_dir, f"{prefix}_fraud_only.json")
    with open(fraud_json_path, "w", encoding="utf-8") as f:
        json.dump(fraud_reviews, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved fraud-only JSON: {fraud_json_path} ({len(fraud_reviews)} records)")

    # Statistics
    stats = generate_statistics(reviews_list)
    stats_path = os.path.join(output_dir, f"{prefix}_statistics.json")
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"[+] Saved statistics: {stats_path}")

    # Print summary
    print("\n" + "="*60)
    print("COLLECTION SUMMARY")
    print("="*60)
    print(f"Total reviews collected:     {stats['total_reviews']}")
    print(f"Fraud-keyword reviews:       {stats['fraud_keyword_reviews']} ({stats['fraud_percentage']}%)")
    print(f"Avg rating (all):            {stats['avg_rating_all']}/5")
    print(f"Avg rating (fraud):          {stats['avg_rating_fraud']}/5")
    print(f"Rating distribution:         {stats['rating_distribution']}")
    print(f"\nPer-app breakdown:")
    for app, count in stats["app_distribution"].items():
        fraud_count = stats["fraud_app_distribution"].get(app, 0)
        print(f"  {app}: {count} total, {fraud_count} fraud-related")
    print(f"\nScam category distribution:")
    for cat, count in stats["category_distribution"].items():
        print(f"  {cat}: {count}")
    print("="*60)

    return stats


def main():
    parser = argparse.ArgumentParser(description="Scrape Google Play reviews for Bangladesh MFS apps")
    parser.add_argument("--app", choices=list(MFS_APPS.keys()), help="Specific app to scrape")
    parser.add_argument("--all", action="store_true", help="Scrape all apps")
    parser.add_argument("--count", type=int, default=5000, help="Max reviews per app (default: 5000)")
    parser.add_argument("--output", default="./app_reviews", help="Output directory")
    parser.add_argument("--lang", default="en", help="Language code (default: en)")
    parser.add_argument("--country", default="us", help="Country code (default: us)")

    args = parser.parse_args()

    if not args.app and not args.all:
        parser.print_help()
        return

    apps_to_scrape = list(MFS_APPS.keys()) if args.all else [args.app]

    all_reviews = []
    for app_key in apps_to_scrape:
        app_info = MFS_APPS[app_key]
        reviews_data = scrape_reviews(
            app_info["package"],
            app_info["display_name"],
            count=args.count,
            lang=args.lang,
            country=args.country
        )
        all_reviews.extend(reviews_data)

    # Save combined results
    stats = save_outputs(all_reviews, args.output, prefix="mfs_app_reviews")
    print(f"\n[*] All done! Output saved to: {args.output}/")


if __name__ == "__main__":
    main()
