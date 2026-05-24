#!/usr/bin/env python3
"""
Stream C: Phishing URL Collection & Infrastructure Analysis Pipeline
Targets: bKash, Nagad, Rocket, DBBL, BRAC Bank phishing URLs

Sources:
  - PhishTank (phishtank.org) - open API
  - OpenPhish (openphish.com) - free feed
  - URLhaus (abuse.ch) - malware/phishing URLs
  - CIRT Bangladesh (cirt.gov.bd) - advisories

Infrastructure enrichment:
  - ASN lookup, hosting country, SSL certificate info
  - Domain age, registrar, name server
  - URL shortener detection

Usage:
    python phishing_pipeline.py --refresh-phishank --enrich
    python phishing_pipeline.py --status-report

Requirements: pip install requests pandas dnspython
"""

import argparse
import csv
import json
import os
import re
import socket
import subprocess
import time
from datetime import datetime
from collections import Counter, defaultdict
from urllib.parse import urlparse

try:
    import requests
    import dns.resolver
except ImportError as e:
    print(f"ERROR: Missing dependency: {e}")
    print("Run: pip install requests dnspython pandas")
    raise


# ============ CONFIGURATION ============

# Bangladesh MFS/banking brand keywords
BD_BRAND_KEYWORDS = [
    'bkash', 'b-kash', 'bksh',
    'nagad', 'ngad',
    'rocket', 'dbbl', 'dutchbangla',
    'brac', 'bracbank',
    'surecash',
    'upay',
    'bangladesh', 'bd',
    'taka', '৳',
    'mfs', 'mobilebanking', 'mobile banking'
]

# URL shortener domains
URL_SHORTENERS = {
    'bit.ly', 'tinyurl.com', 't.co', 'goo.gl', 'ow.ly',
    'short.link', 'rebrand.ly', 'cutt.ly', 'rb.gy',
    'shorturl.at', 'is.gd', 'buff.ly', 'dlvr.it',
    'tr.im', 'cli.gs', 'po.st', 'su.pr', 'bc.vc',
    's.id', 'short.io', 'bl.ink', 't2m.io',
    # Bangladesh-specific shorteners
    'bdlink.xyz', 'bdsite.link', 'takaoffer.com'
}

# Common TLDs abused in BD phishing
SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.xyz', '.online', '.site', '.club', '.link']

# Output schema
URL_SCHEMA = [
    "url_id", "url", "domain", "subdomain", "tld",
    "source", "brand_targeted", "first_seen", "last_seen",
    "is_verified_phishing", "is_online",
    "hosting_asn", "hosting_country", "hosting_ip",
    "registrar", "domain_creation_date", "domain_age_days",
    "has_https", "url_length", "uses_url_shortener",
    "redirect_chain_length", "page_title",
    " collected_at", "enrichment_status"
]


class PhishingPipeline:
    def __init__(self, output_dir="./phishing_data"):
        self.output_dir = output_dir
        self.raw_dir = os.path.join(output_dir, "raw")
        self.enriched_dir = os.path.join(output_dir, "enriched")
        self.reports_dir = os.path.join(output_dir, "reports")

        for d in [self.raw_dir, self.enriched_dir, self.reports_dir]:
            os.makedirs(d, exist_ok=True)

        self.brand_pattern = re.compile(
            r'(' + '|'.join(re.escape(k) for k in BD_BRAND_KEYWORDS) + r')',
            re.IGNORECASE
        )

    def is_bd_brand_related(self, url):
        """Check if URL targets Bangladesh MFS/banking brands."""
        url_lower = url.lower()
        return bool(self.brand_pattern.search(url_lower))

    def extract_domain_info(self, url):
        """Extract domain components from URL."""
        try:
            parsed = urlparse(url if '://' in url else 'http://' + url)
            hostname = parsed.hostname or ''
            parts = hostname.split('.')

            if len(parts) >= 2:
                tld = '.' + parts[-1] if len(parts) == 2 else '.' + '.'.join(parts[-2:])
                domain = '.'.join(parts[-2:])
                subdomain = '.'.join(parts[:-2]) if len(parts) > 2 else ''
            else:
                tld = ''
                domain = hostname
                subdomain = ''

            return {
                'domain': domain,
                'subdomain': subdomain,
                'tld': tld,
                'hostname': hostname
            }
        except Exception:
            return {'domain': '', 'subdomain': '', 'tld': '', 'hostname': ''}

    def identify_brand_target(self, url, page_title=''):
        """Identify which Bangladesh brand is being targeted."""
        combined = (url + ' ' + page_title).lower()
        brands = []
        if any(k in combined for k in ['bkash', 'b-kash', 'bksh']):
            brands.append('bKash')
        if any(k in combined for k in ['nagad', 'ngad']):
            brands.append('Nagad')
        if any(k in combined for k in ['rocket', 'dbbl', 'dutchbangla']):
            brands.append('Rocket/DBBL')
        if 'brac' in combined:
            brands.append('BRAC Bank')
        if 'surecash' in combined:
            brands.append('SureCash')
        if 'upay' in combined:
            brands.append('Upay')
        return '|'.join(brands) if brands else 'unknown'

    def is_url_shortened(self, url):
        """Detect if URL uses a known shortener."""
        try:
            parsed = urlparse(url if '://' in url else 'http://' + url)
            return parsed.hostname in URL_SHORTENERS
        except Exception:
            return False

    # ============ DATA SOURCE: PHISHTANK ============

    def fetch_phishtank_data(self):
        """Download PhishTank database."""
        print("[+] Fetching PhishTank data...")
        phishtank_url = "http://data.phishtank.com/data/online-valid.json"
        # Note: Requires registration for full data
        # Free tier: limited access

        output_file = os.path.join(self.raw_dir, f"phishtank_{datetime.now().strftime('%Y%m%d')}.json")

        try:
            resp = requests.get(phishtank_url, timeout=120)
            if resp.status_code == 200:
                data = resp.json()
                with open(output_file, 'w') as f:
                    json.dump(data, f)
                print(f"    [✓] Downloaded {len(data)} entries")
                return data
            else:
                print(f"    [!] PhishTank returned status {resp.status_code}")
                print(f"    [!] You may need to register at phishtank.org for API access")
                return []
        except Exception as e:
            print(f"    [!] Error fetching PhishTank: {e}")
            return []

    def filter_phishtank_bd(self, phishtank_data):
        """Filter PhishTank entries for Bangladesh brands."""
        print("[+] Filtering PhishTank for BD brand targets...")
        filtered = []
        for entry in phishtank_data:
            url = entry.get('url', '')
            if self.is_bd_brand_related(url):
                domain_info = self.extract_domain_info(url)
                filtered.append({
                    'url_id': entry.get('phish_id', ''),
                    'url': url,
                    'domain': domain_info['domain'],
                    'subdomain': domain_info['subdomain'],
                    'tld': domain_info['tld'],
                    'source': 'PhishTank',
                    'brand_targeted': self.identify_brand_target(url, entry.get('phish_detail_page', '')),
                    'first_seen': entry.get('submission_time', ''),
                    'last_seen': entry.get('verified_at', ''),
                    'is_verified_phishing': entry.get('verified', 'unknown'),
                    'is_online': entry.get('online', 'unknown'),
                    'details_page': entry.get('phish_detail_page', ''),
                    'collected_at': datetime.now().isoformat(),
                    'enrichment_status': 'pending'
                })
        print(f"    [✓] Found {len(filtered)} BD-related phishing URLs")
        return filtered

    # ============ DATA SOURCE: OPENPHISH ============

    def fetch_openphish_feed(self):
        """Download OpenPhish free feed."""
        print("[+] Fetching OpenPhish feed...")
        openphish_url = "https://openphish.com/feed.txt"

        output_file = os.path.join(self.raw_dir, f"openphish_{datetime.now().strftime('%Y%m%d')}.txt")

        try:
            resp = requests.get(openphish_url, timeout=60)
            if resp.status_code == 200:
                urls = [u.strip() for u in resp.text.strip().split('\n') if u.strip()]
                with open(output_file, 'w') as f:
                    f.write('\n'.join(urls))
                print(f"    [✓] Downloaded {len(urls)} URLs")
                return urls
            else:
                print(f"    [!] OpenPhish returned status {resp.status_code}")
                return []
        except Exception as e:
            print(f"    [!] Error fetching OpenPhish: {e}")
            return []

    def filter_openphish_bd(self, urls):
        """Filter OpenPhish URLs for Bangladesh brands."""
        print("[+] Filtering OpenPhish for BD brand targets...")
        filtered = []
        seen_domains = set()

        for url in urls:
            if self.is_bd_brand_related(url):
                domain_info = self.extract_domain_info(url)
                domain_key = domain_info['domain']

                # Deduplicate by domain
                if domain_key not in seen_domains:
                    seen_domains.add(domain_key)
                    filtered.append({
                        'url_id': f"op_{abs(hash(url)) % 100000000:08d}",
                        'url': url,
                        'domain': domain_info['domain'],
                        'subdomain': domain_info['subdomain'],
                        'tld': domain_info['tld'],
                        'source': 'OpenPhish',
                        'brand_targeted': self.identify_brand_target(url),
                        'first_seen': datetime.now().isoformat(),
                        'last_seen': datetime.now().isoformat(),
                        'is_verified_phishing': 'yes',
                        'is_online': 'unknown',
                        'collected_at': datetime.now().isoformat(),
                        'enrichment_status': 'pending'
                    })

        print(f"    [✓] Found {len(filtered)} BD-related URLs")
        return filtered

    # ============ DATA SOURCE: URLHAUS ============

    def fetch_urlhaus_data(self):
        """Fetch recent URLhaus entries."""
        print("[+] Fetching URLhaus recent URLs...")
        urlhaus_url = "https://urlhaus-api.abuse.ch/v1/urls/recent/"

        try:
            resp = requests.get(urlhaus_url, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                urls_data = data.get('urls', [])
                print(f"    [✓] Downloaded {len(urls_data)} entries")
                return urls_data
            else:
                print(f"    [!] URLhaus returned status {resp.status_code}")
                return []
        except Exception as e:
            print(f"    [!] Error fetching URLhaus: {e}")
            return []

    def filter_urlhaus_bd(self, urlhaus_data):
        """Filter URLhaus for Bangladesh brand targets."""
        print("[+] Filtering URLhaus for BD brand targets...")
        filtered = []
        for entry in urlhaus_data:
            url = entry.get('url', '')
            if self.is_bd_brand_related(url):
                domain_info = self.extract_domain_info(url)
                filtered.append({
                    'url_id': f"uh_{entry.get('id', '')}",
                    'url': url,
                    'domain': domain_info['domain'],
                    'subdomain': domain_info['subdomain'],
                    'tld': domain_info['tld'],
                    'source': 'URLhaus',
                    'brand_targeted': self.identify_brand_target(url),
                    'first_seen': entry.get('date_added', ''),
                    'last_seen': entry.get('last_seen', ''),
                    'is_verified_phishing': 'yes',
                    'is_online': 'yes' if entry.get('status') == 'online' else 'no',
                    'hosting_ip': entry.get('host', ''),
                    'collected_at': datetime.now().isoformat(),
                    'enrichment_status': 'partial'  # Already has IP
                })
        print(f"    [✓] Found {len(filtered)} BD-related URLs")
        return filtered

    # ============ INFRASTRUCTURE ENRICHMENT ============

    def enrich_asn_info(self, ip_address):
        """Look up ASN and hosting country for an IP."""
        try:
            # Using IPinfo.io free API (no key needed for basic)
            resp = requests.get(f"https://ipinfo.io/{ip_address}/json", timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                org = data.get('org', '')
                # Extract ASN from org string like "AS12345 Example ISP"
                asn_match = re.search(r'AS(\d+)', org)
                return {
                    'hosting_asn': f"AS{asn_match.group(1)}" if asn_match else org,
                    'hosting_country': data.get('country', ''),
                    'hosting_ip': ip_address
                }
        except Exception:
            pass
        return {'hosting_asn': '', 'hosting_country': '', 'hosting_ip': ip_address}

    def dns_lookup(self, domain):
        """Resolve domain to IP address."""
        try:
            answers = dns.resolver.resolve(domain, 'A')
            return [str(rdata) for rdata in answers]
        except Exception:
            return []

    def enrich_entry(self, entry):
        """Enrich a single URL entry with infrastructure data."""
        domain = entry.get('domain', '')
        url = entry.get('url', '')

        if not domain:
            entry['enrichment_status'] = 'failed_no_domain'
            return entry

        # DNS resolution
        ips = self.dns_lookup(domain)
        if ips:
            entry['hosting_ip'] = ips[0]
            # ASN lookup
            asn_info = self.enrich_asn_info(ips[0])
            entry.update(asn_info)

        # URL characteristics
        entry['url_length'] = len(url)
        entry['has_https'] = url.startswith('https://')
        entry['uses_url_shortener'] = self.is_url_shortened(url)

        entry['enrichment_status'] = 'enriched'
        return entry

    def enrich_all(self, entries, delay=1):
        """Enrich all entries with rate limiting."""
        print(f"[+] Enriching {len(entries)} entries with infrastructure data...")
        enriched = []
        for i, entry in enumerate(entries):
            if i % 10 == 0:
                print(f"    -> Enriched {i}/{len(entries)}...")
            enriched_entry = self.enrich_entry(entry)
            enriched.append(enriched_entry)
            time.sleep(delay)  # Rate limiting
        print(f"    [✓] Enrichment complete")
        return enriched

    # ============ REPORTING ============

    def generate_infrastructure_report(self, entries):
        """Generate infrastructure analysis report."""
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_urls': len(entries),
            'by_source': dict(Counter(e.get('source', 'unknown') for e in entries)),
            'by_brand': dict(Counter(e.get('brand_targeted', 'unknown') for e in entries)),
            'by_tld': dict(Counter(e.get('tld', 'unknown') for e in entries)),
            'by_hosting_country': dict(Counter(e.get('hosting_country', 'unknown') for e in entries)),
            'by_asn': dict(Counter(e.get('hosting_asn', 'unknown') for e in entries)),
            'https_adoption': sum(1 for e in entries if e.get('has_https')) / len(entries) * 100 if entries else 0,
            'shortener_usage': sum(1 for e in entries if e.get('uses_url_shortener')) / len(entries) * 100 if entries else 0,
            'top_domains': dict(Counter(e.get('domain', '') for e in entries).most_common(20)),
        }

        report_path = os.path.join(self.reports_dir, f"infrastructure_report_{datetime.now().strftime('%Y%m%d')}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"[+] Infrastructure report saved: {report_path}")

        # Print summary
        print("\n" + "="*60)
        print("INFRASTRUCTURE ANALYSIS SUMMARY")
        print("="*60)
        print(f"Total URLs analyzed:    {report['total_urls']}")
        print(f"By source:              {report['by_source']}")
        print(f"By brand targeted:      {report['by_brand']}")
        print(f"HTTPS adoption:         {report['https_adoption']:.1f}%")
        print(f"URL shortener usage:    {report['shortener_usage']:.1f}%")
        print(f"\nTop TLDs: {dict(list(report['by_tld'].items())[:10])}")
        print(f"\nTop hosting countries: {dict(list(report['by_hosting_country'].items())[:10])}")
        print("="*60)

        return report

    def save_entries(self, entries, prefix="phishing_urls"):
        """Save entries to JSON and CSV."""
        # JSON
        json_path = os.path.join(self.enriched_dir, f"{prefix}.json")
        with open(json_path, 'w') as f:
            json.dump(entries, f, indent=2)
        print(f"[+] Saved JSON: {json_path}")

        # CSV
        csv_path = os.path.join(self.enriched_dir, f"{prefix}.csv")
        if entries:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=URL_SCHEMA)
                writer.writeheader()
                for e in entries:
                    row = {k: e.get(k, '') for k in URL_SCHEMA}
                    writer.writerow(row)
            print(f"[+] Saved CSV: {csv_path}")


def main():
    parser = argparse.ArgumentParser(description="Bangladesh MFS Phishing URL Pipeline")
    parser.add_argument("--output", default="./phishing_data", help="Output directory")
    parser.add_argument("--refresh-phishtank", action="store_true", help="Fetch fresh PhishTank data")
    parser.add_argument("--refresh-openphish", action="store_true", help="Fetch fresh OpenPhish feed")
    parser.add_argument("--refresh-urlhaus", action="store_true", help="Fetch fresh URLhaus data")
    parser.add_argument("--refresh-all", action="store_true", help="Fetch all sources")
    parser.add_argument("--enrich", action="store_true", help="Enrich with infrastructure data")
    parser.add_argument("--status-report", action="store_true", help="Generate status report from existing data")
    parser.add_argument("--delay", type=int, default=1, help="Delay between enrichment requests (seconds)")

    args = parser.parse_args()

    pipeline = PhishingPipeline(output_dir=args.output)

    if args.status_report:
        # Load existing data and generate report
        json_path = os.path.join(pipeline.enriched_dir, "phishing_urls.json")
        if os.path.exists(json_path):
            with open(json_path) as f:
                entries = json.load(f)
            pipeline.generate_infrastructure_report(entries)
        else:
            print("[!] No existing data found. Run collection first.")
        return

    all_entries = []

    # Fetch from sources
    if args.refresh_phishtank or args.refresh_all:
        pt_data = pipeline.fetch_phishtank_data()
        if pt_data:
            pt_filtered = pipeline.filter_phishtank_bd(pt_data)
            all_entries.extend(pt_filtered)

    if args.refresh_openphish or args.refresh_all:
        op_urls = pipeline.fetch_openphish_feed()
        if op_urls:
            op_filtered = pipeline.filter_openphish_bd(op_urls)
            all_entries.extend(op_filtered)

    if args.refresh_urlhaus or args.refresh_all:
        uh_data = pipeline.fetch_urlhaus_data()
        if uh_data:
            uh_filtered = pipeline.filter_urlhaus_bd(uh_data)
            all_entries.extend(uh_filtered)

    if not all_entries:
        print("[!] No entries collected. Use --refresh-all to fetch data.")
        return

    # Enrich
    if args.enrich:
        all_entries = pipeline.enrich_all(all_entries, delay=args.delay)

    # Save
    pipeline.save_entries(all_entries)

    # Report
    pipeline.generate_infrastructure_report(all_entries)

    print(f"\n[*] Pipeline complete! Data saved to: {args.output}/")


if __name__ == "__main__":
    main()
