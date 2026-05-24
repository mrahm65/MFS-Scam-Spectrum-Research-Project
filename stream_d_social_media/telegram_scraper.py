#!/usr/bin/env python3
"""
Telegram Public Channel Scraper for MFS Fraud Research
Scrapes public Telegram channels via t.me/s/CHANNEL (no login required)

Usage:
    python telegram_scraper.py --channel LGPaymentgateway
    python telegram_scraper.py --list channels.txt
    python telegram_scraper.py --all-known --output ./telegram_data

Requirements: pip install requests beautifulsoup4 lxml
"""

import argparse
import csv
import json
import os
import re
import time
from datetime import datetime
from collections import Counter

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: pip install requests beautifulsoup4 lxml")
    raise

# Known channels from research - BD MFS payment/fraud related
KNOWN_CHANNELS = [
    "LGPaymentgateway",    # Payment gateway supporting bKash/Nagad
    "ag4566",              # OKEXPAY - bKash/Nagad payment channel
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

BD_PHONE_RE = re.compile(r'\b(?:\+?8801|01)[3-9]\d{8}\b')
URL_RE = re.compile(r'https?://[^\s<>"{}|\\^`[\]]+')


class TelegramScraper:
    def __init__(self, output_dir="./telegram_data"):
        self.output_dir = output_dir
        self.raw_dir = os.path.join(output_dir, "raw")
        self.processed_dir = os.path.join(output_dir, "processed")
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def get_posts(self, channel_name, max_posts=None):
        all_posts = []
        before_id = None
        count = 0
        print(f"[+] Scraping @{channel_name}")

        while True:
            url = f"https://t.me/s/{channel_name}"
            if before_id:
                url += f"?before={before_id}"
            try:
                resp = self.session.get(url, timeout=30)
                if resp.status_code != 200:
                    print(f"    [!] HTTP {resp.status_code}")
                    break
                posts, last_id = self._parse(resp.text, channel_name)
                if not posts:
                    print(f"    -> No more posts")
                    break
                all_posts.extend(posts)
                count += len(posts)
                before_id = last_id
                print(f"    -> {count} posts...")
                if max_posts and count >= max_posts:
                    all_posts = all_posts[:max_posts]
                    break
                time.sleep(1.5)
            except Exception as e:
                print(f"    [!] Error: {e}")
                break

        print(f"[+] @{channel_name}: {len(all_posts)} posts total")
        return all_posts

    def _parse(self, html, channel_name):
        soup = BeautifulSoup(html, 'lxml')
        posts = []
        last_id = None

        for div in soup.find_all('div', class_='tgme_widget_message'):
            try:
                post = {'channel': channel_name, 'scraped_at': datetime.now().isoformat()}
                # Message ID
                data_post = div.get('data-post', '')
                post['message_id'] = data_post.split('/')[-1] if '/' in data_post else data_post
                if post['message_id']:
                    last_id = post['message_id']
                # Timestamp
                time_el = div.find('time', class_='time')
                post['timestamp'] = time_el.get('datetime', '') if time_el else ''
                post['date_display'] = time_el.text.strip() if time_el and time_el.text else ''
                # Text
                text_el = div.find('div', class_='tgme_widget_message_text')
                post['text'] = text_el.get_text(separator='\n').strip() if text_el else ''
                post['has_text'] = bool(post['text'])
                # Views
                views_el = div.find('span', class_='tgme_widget_message_views')
                post['views'] = self._parse_views(views_el.text.strip()) if views_el else None
                # Media
                photo = div.find('a', class_='tgme_widget_message_photo_wrap')
                post['has_photo'] = bool(photo)
                video = div.find('div', class_='tgme_widget_message_video')
                post['has_video'] = bool(video)
                # Forward
                fwd = div.find('a', class_='tgme_widget_message_forwarded_from_name')
                post['forwarded_from'] = fwd.text.strip() if fwd else ''
                # Reply
                post['is_reply'] = bool(div.find('a', class_='tgme_widget_message_reply'))
                # Enrichment
                post = self._enrich(post)
                posts.append(post)
            except Exception:
                continue
        return posts, last_id

    def _parse_views(self, t):
        if not t: return None
        t = t.replace(',', '')
        if 'K' in t: return int(float(t.replace('K', '')) * 1000)
        if 'M' in t: return int(float(t.replace('M', '')) * 1000000)
        try: return int(t)
        except: return None

    def _enrich(self, post):
        text = post.get('text', '').lower()
        post['mentions_bkash'] = 'bkash' in text
        post['mentions_nagad'] = 'nagad' in text
        post['mentions_rocket'] = 'rocket' in text
        post['mentions_bangladesh'] = 'bangladesh' in text or '\u09ac\u09be\u0982\u09b2\u09be\u09a6\u09c7\u09b6' in text
        fraud_kws = ['scam', 'fraud', 'hack', 'otp', 'phishing', 'free money', 'bonus', 'lottery', 'prize', 'investment', 'processing fee', 'agent', 'deposit', 'payout', 'guaranteed']
        post['has_fraud_keyword'] = any(kw in text for kw in fraud_kws)
        post['fraud_keywords_found'] = [kw for kw in fraud_kws if kw in text]
        post['has_url'] = bool(URL_RE.search(text))
        post['urls_found'] = URL_RE.findall(text)
        post['has_phone'] = bool(BD_PHONE_RE.search(text))
        post['phones_found'] = BD_PHONE_RE.findall(text)
        post['has_username'] = bool(re.search(r'@\w+', text))
        post['has_bangla'] = bool(re.search(r'[\u0980-\u09FF]', text))
        post['word_count'] = len(text.split())
        return post

    def save(self, posts, channel_name):
        ts = datetime.now().strftime('%Y%m%d')
        jpath = os.path.join(self.raw_dir, f"{channel_name}_{ts}.json")
        with open(jpath, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        print(f"    [+] JSON: {jpath}")
        if posts:
            cpath = os.path.join(self.processed_dir, f"{channel_name}_{ts}.csv")
            keys = ['message_id', 'channel', 'timestamp', 'date_display', 'text', 'views',
                    'has_photo', 'has_video', 'forwarded_from', 'is_reply',
                    'mentions_bkash', 'mentions_nagad', 'mentions_rocket',
                    'has_fraud_keyword', 'has_url', 'has_phone', 'has_username',
                    'has_bangla', 'word_count', 'scraped_at']
            with open(cpath, 'w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=keys)
                w.writeheader()
                for p in posts:
                    w.writerow({k: p.get(k, '') for k in keys})
            print(f"    [+] CSV: {cpath}")

    def report(self, all_posts):
        r = {
            'generated_at': datetime.now().isoformat(),
            'total_posts': len(all_posts),
            'brand_mentions': {
                'bKash': sum(1 for p in all_posts if p.get('mentions_bkash')),
                'Nagad': sum(1 for p in all_posts if p.get('mentions_nagad')),
                'Rocket': sum(1 for p in all_posts if p.get('mentions_rocket')),
            },
            'fraud_posts': sum(1 for p in all_posts if p.get('has_fraud_keyword')),
            'with_urls': sum(1 for p in all_posts if p.get('has_url')),
            'with_phone': sum(1 for p in all_posts if p.get('has_phone')),
            'with_bangla': sum(1 for p in all_posts if p.get('has_bangla')),
        }
        rpath = os.path.join(self.output_dir, "collection_report.json")
        with open(rpath, 'w') as f:
            json.dump(r, f, indent=2)
        print(f"\n{'='*60}")
        print("TELEGRAM COLLECTION REPORT")
        print(f"{'='*60}")
        for k, v in r.items():
            print(f"  {k}: {v}")
        print(f"{'='*60}")
        return r


def main():
    p = argparse.ArgumentParser(description="Telegram Public Channel Scraper")
    p.add_argument("--channel", help="Single channel (no @)")
    p.add_argument("--list", help="File with channel names")
    p.add_argument("--all-known", action="store_true", help="Scrape all known channels")
    p.add_argument("--max-posts", type=int, help="Max posts per channel")
    p.add_argument("--output", default="./telegram_data", help="Output directory")
    args = p.parse_args()

    scraper = TelegramScraper(output_dir=args.output)
    all_posts = []

    channels = []
    if args.channel:
        channels.append(args.channel)
    if args.list:
        with open(args.list) as f:
            channels.extend([l.strip() for l in f if l.strip()])
    if args.all_known:
        channels.extend(KNOWN_CHANNELS)

    for ch in channels:
        posts = scraper.get_posts(ch, max_posts=args.max_posts)
        scraper.save(posts, ch)
        all_posts.extend(posts)
        time.sleep(2)

    if all_posts:
        scraper.report(all_posts)
    print(f"\n[*] Done! Output: {args.output}/")


if __name__ == "__main__":
    main()
