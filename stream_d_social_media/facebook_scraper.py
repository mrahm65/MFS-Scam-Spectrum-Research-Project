#!/usr/bin/env python3
"""
Facebook Public Page Scraper for MFS Fraud Research
Scrapes public Facebook pages without authentication.
Only works for PUBLIC pages - cannot access private groups or profiles.

Uses requests + BeautifulSoup for static content.
For dynamic (JS-rendered) content, use --selenium mode.

Usage:
    python facebook_scraper.py --page "bkash" --output ./facebook_data
    python facebook_scraper.py --list pages.txt --selenium
    python facebook_scraper.py --search-terms "bKash offer,Nagad bonus" --discover

Requirements:
    Basic: pip install requests beautifulsoup4
    Selenium: pip install selenium webdriver-manager
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
    print("ERROR: pip install requests beautifulsoup4")
    raise

# Bangladesh MFS fraud-related search terms
SEARCH_TERMS = [
    "bKash offer", "bKash bonus", "bKash free", "bKash cashback",
    "Nagad offer", "Nagad bonus", "Nagad free", "Nagad cashback",
    "free taka", "taka bonus", "mobile banking offer",
    "বিকাশ অফার", "নগদ বোনাস", "ফ্রি টাকা",
]

# Known public pages to investigate (from news/research)
TARGET_PAGES = [
    # These are example page names - verify they exist and are public
    # before scraping. Replace with actual page URLs you discover.
]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
}

# Pattern to detect scam indicators in post text
SCAM_PATTERNS = [
    r'\bfree\b.*\btaka\b', r'\bbonus\b.*\bbkash\b|\bbkash\b.*\bbonus\b',
    r'\bcashback\b', r'\blottery\b', r'\bwon\b.*\b\d+\b',
    r'\bsend\b.*\bOTP\b|\bOTP\b.*\bsend\b',
    r'\bclick\b.*\blink\b|\bclick\b.*\bhere\b',
    r'\bverify\b.*\baccount\b|\baccount\b.*\bverify\b',
    r'\blimited\b.*\btime\b', r'\bhurry\b', r'\bact\b.*\bnow\b',
    r'https?://\S+\.tk\b', r'https?://\S+\.xyz\b',
    r'https?://\S+bit\.ly\S*', r'https?://\S+tinyurl\S*',
]
SCAM_RE = [re.compile(p, re.IGNORECASE) for p in SCAM_PATTERNS]


class FacebookScraper:
    def __init__(self, output_dir="./facebook_data"):
        self.output_dir = output_dir
        self.raw_dir = os.path.join(output_dir, "raw")
        self.processed_dir = os.path.join(output_dir, "processed")
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.processed_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def scrape_page_posts(self, page_name, max_posts=50, use_selenium=False):
        """
        Scrape posts from a public Facebook page.
        Note: Facebook heavily rate-limits and may block automated requests.
        Use selenium mode for better results.
        """
        if use_selenium:
            return self._scrape_selenium(page_name, max_posts)
        return self._scrape_requests(page_name, max_posts)

    def _scrape_requests(self, page_name, max_posts):
        """Scrape using requests (limited - Facebook blocks this often)."""
        print(f"[+] Scraping Facebook page: {page_name} (requests mode)")
        print("    [!] WARNING: Facebook often blocks requests-based scraping.")
        print("    [!] Use --selenium for better results.")

        url = f"https://www.facebook.com/{page_name}/posts"
        posts = []

        try:
            resp = self.session.get(url, timeout=30)
            if resp.status_code != 200:
                print(f"    [!] HTTP {resp.status_code} - Facebook may be blocking")
                return posts

            soup = BeautifulSoup(resp.text, 'lxml')
            # Facebook's HTML structure changes frequently
            # These selectors may need updating
            for article in soup.find_all('div', {'data-ad-preview': 'message'}):
                post = self._extract_post(article, page_name)
                if post:
                    posts.append(post)
                    if len(posts) >= max_posts:
                        break

        except Exception as e:
            print(f"    [!] Error: {e}")

        print(f"    [+] Collected {len(posts)} posts")
        return posts

    def _scrape_selenium(self, page_name, max_posts):
        """Scrape using Selenium (handles JS-rendered content)."""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
        except ImportError:
            print("ERROR: pip install selenium webdriver-manager")
            return []

        print(f"[+] Scraping Facebook page: {page_name} (selenium mode)")
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        driver = None
        posts = []

        try:
            driver = webdriver.Chrome(options=options)
            driver.get(f"https://www.facebook.com/{page_name}/posts")
            time.sleep(5)  # Wait for JS render

            # Scroll to load more posts
            for _ in range(min(max_posts // 5, 20)):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(3)

            # Extract posts - Facebook's selectors change frequently
            html = driver.page_source
            soup = BeautifulSoup(html, 'lxml')

            # Try multiple selectors
            selectors = [
                'div[data-ad-preview="message"]',
                'div.x1yztbdb div.x1iorvi4',
                'div[role="article"]',
            ]

            for selector in selectors:
                elements = soup.select(selector)
                for el in elements:
                    post = self._extract_post(el, page_name)
                    if post and post not in posts:
                        posts.append(post)
                    if len(posts) >= max_posts:
                        break
                if len(posts) >= 10:
                    break

        except Exception as e:
            print(f"    [!] Selenium error: {e}")
        finally:
            if driver:
                driver.quit()

        print(f"    [+] Collected {len(posts)} posts")
        return posts

    def _extract_post(self, element, page_name):
        """Extract post data from a BeautifulSoup element."""
        post = {
            'page': page_name,
            'scraped_at': datetime.now().isoformat(),
            'source_url': f"https://facebook.com/{page_name}",
        }

        # Post text
        text = ''
        # Try multiple text container patterns
        for selector in ['span.x1iorvi4', 'div.x11i5rnm', 'div.xt0psk2', 'div']:
            text_el = element.select_one(selector) if hasattr(element, 'select_one') else None
            if text_el and text_el.text.strip():
                text = text_el.get_text(separator='\n').strip()
                if len(text) > 20:
                    break

        if not text:
            text = element.get_text(separator='\n').strip() if hasattr(element, 'get_text') else ''

        post['text'] = text
        post['word_count'] = len(text.split())

        # Skip if too short
        if len(text) < 10:
            return None

        # Check for scam indicators
        post['scam_indicators'] = [i for i, p in enumerate(SCAM_RE) if p.search(text)]
        post['has_scam_indicator'] = bool(post['scam_indicators'])

        # URLs
        urls = re.findall(r'https?://[^\s<>"{}|\\^`[\]]+', text)
        post['urls'] = urls
        post['has_url'] = bool(urls)

        # Phone numbers
        phones = re.findall(r'\b(?:\+?8801|01)[3-9]\d{8}\b', text)
        post['phones'] = phones
        post['has_phone'] = bool(phones)

        # Brand mentions
        tl = text.lower()
        post['mentions_bkash'] = 'bkash' in tl
        post['mentions_nagad'] = 'nagad' in tl
        post['mentions_rocket'] = 'rocket' in tl

        # Bangla
        post['has_bangla'] = bool(re.search(r'[\u0980-\u09FF]', text))

        return post

    def search_public_pages(self, query, limit=10):
        """
        Search for public pages. Returns search results.
        Note: Facebook search requires authentication.
        This uses Google search as a workaround.
        """
        print(f"[+] Searching for public pages: '{query}'")
        print("    [!] Using Google search workaround (limited)")

        search_query = f"site:facebook.com/pages {query} Bangladesh"
        results = []

        try:
            from urllib.parse import quote_plus
            url = f"https://www.google.com/search?q={quote_plus(search_query)}"
            resp = self.session.get(url, timeout=30)

            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, 'lxml')
                for g in soup.find_all('div', class_='g'):
                    link = g.find('a')
                    if link and 'facebook.com' in link.get('href', ''):
                        title = g.find('h3')
                        results.append({
                            'url': link['href'],
                            'title': title.text if title else '',
                        })
                    if len(results) >= limit:
                        break
        except Exception as e:
            print(f"    [!] Search error: {e}")

        print(f"    [+] Found {len(results)} potential pages")
        return results

    def save(self, posts, page_name):
        ts = datetime.now().strftime('%Y%m%d')
        jpath = os.path.join(self.raw_dir, f"{page_name}_{ts}.json")
        with open(jpath, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        print(f"    [+] JSON: {jpath}")

        if posts:
            cpath = os.path.join(self.processed_dir, f"{page_name}_{ts}.csv")
            keys = ['page', 'text', 'word_count', 'has_scam_indicator',
                    'has_url', 'has_phone', 'mentions_bkash', 'mentions_nagad',
                    'has_bangla', 'urls', 'phones', 'scraped_at', 'source_url']
            with open(cpath, 'w', encoding='utf-8', newline='') as f:
                w = csv.DictWriter(f, fieldnames=keys)
                w.writeheader()
                for p in posts:
                    row = {k: p.get(k, '') for k in keys}
                    row['urls'] = '|'.join(row['urls']) if isinstance(row['urls'], list) else row['urls']
                    row['phones'] = '|'.join(row['phones']) if isinstance(row['phones'], list) else row['phones']
                    w.writerow(row)
            print(f"    [+] CSV: {cpath}")

    def report(self, all_posts):
        r = {
            'generated_at': datetime.now().isoformat(),
            'total_posts': len(all_posts),
            'scam_posts': sum(1 for p in all_posts if p.get('has_scam_indicator')),
            'with_urls': sum(1 for p in all_posts if p.get('has_url')),
            'with_phone': sum(1 for p in all_posts if p.get('has_phone')),
            'brand_mentions': {
                'bKash': sum(1 for p in all_posts if p.get('mentions_bkash')),
                'Nagad': sum(1 for p in all_posts if p.get('mentions_nagad')),
                'Rocket': sum(1 for p in all_posts if p.get('mentions_rocket')),
            }
        }
        rpath = os.path.join(self.output_dir, "collection_report.json")
        with open(rpath, 'w') as f:
            json.dump(r, f, indent=2)
        print(f"\n{'='*60}")
        print("FACEBOOK COLLECTION REPORT")
        for k, v in r.items():
            print(f"  {k}: {v}")
        print(f"{'='*60}")
        return r


def main():
    p = argparse.ArgumentParser(description="Facebook Public Page Scraper")
    p.add_argument("--page", help="Page name/URL")
    p.add_argument("--list", help="File with page names")
    p.add_argument("--search-terms", help="Comma-separated search terms")
    p.add_argument("--discover", action="store_true", help="Discover pages via search")
    p.add_argument("--selenium", action="store_true", help="Use Selenium (better but slower)")
    p.add_argument("--max-posts", type=int, default=50)
    p.add_argument("--output", default="./facebook_data")
    args = p.parse_args()

    scraper = FacebookScraper(output_dir=args.output)
    all_posts = []

    if args.discover and args.search_terms:
        terms = [t.strip() for t in args.search_terms.split(',')]
        for term in terms:
            results = scraper.search_public_pages(term)
            for res in results:
                print(f"    Found: {res['title']} -> {res['url']}")

    pages = []
    if args.page:
        pages.append(args.page)
    if args.list:
        with open(args.list) as f:
            pages.extend([l.strip() for l in f if l.strip()])

    for pg in pages:
        posts = scraper.scrape_page_posts(pg, max_posts=args.max_posts, use_selenium=args.selenium)
        scraper.save(posts, pg)
        all_posts.extend(posts)
        time.sleep(5)

    if all_posts:
        scraper.report(all_posts)
    print(f"\n[*] Done! Output: {args.output}/")


if __name__ == "__main__":
    main()
