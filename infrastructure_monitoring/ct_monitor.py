#!/usr/bin/env python3
"""
Infrastructure Monitoring: Certificate Transparency Log Scraper
Monitors SSL certificate issuance for Bangladesh MFS brand domains.
Uses crt.sh and CertStream for early phishing detection.

Usage:
    python ct_monitor.py --brands bkash,nagad,rocket --days 30
    python ct_monitor.py --stream  # Real-time CertStream monitoring

Requirements: pip install requests certstream
"""

import argparse
import csv
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta
from collections import defaultdict

try:
    import requests
except ImportError:
    print("ERROR: pip install requests")
    raise


# ============ CONFIGURATION ============

BD_MFS_BRANDS = {
    'bkash': ['bkash', 'b-kash', 'bksh', 'বিকাশ'],
    'nagad': ['nagad', 'ngad', 'নগদ'],
    'rocket': ['rocket', 'dbblmobile', 'dutchbangla'],
    'brac': ['bracbank', 'brac bank'],
    'surecash': ['surecash'],
    'upay': ['upay'],
}

SUSPICIOUS_KEYWORDS = [
    'login', 'signin', 'verify', 'secure', 'account', 'update',
    'confirm', 'validation', 'auth', 'wallet', 'payment',
    'free', 'offer', 'bonus', 'cashback', 'prize', 'win',
    'login-bkash', 'bkash-login', 'nagad-verify', 'secure-dbbl',
    'bkash-secure', 'nagad-secure', 'bkash-update', 'nagad-update',
]

SUSPICIOUS_TLDS = ['.tk', '.ml', '.ga', '.cf', '.gq', '.top', '.xyz', 
                   '.online', '.site', '.club', '.link', '.work', '.party']


class CTLogMonitor:
    def __init__(self, output_dir="./ct_monitor"):
        self.output_dir = output_dir
        self.raw_dir = os.path.join(output_dir, "raw")
        self.alerts_dir = os.path.join(output_dir, "alerts")
        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs(self.alerts_dir, exist_ok=True)

        self.suspicious_domains = []

    def query_crtsh(self, domain, subdomains=True, match='all'):
        """Query crt.sh for certificates matching a domain."""
        url = "https://crt.sh/"
        params = {
            'q': f'%.{domain}' if subdomains else domain,
            'output': 'json',
            'match': match,
        }

        try:
            resp = requests.get(url, params=params, timeout=60)
            if resp.status_code == 200:
                return resp.json()
            else:
                print(f"    [!] crt.sh returned {resp.status_code}")
                return []
        except Exception as e:
            print(f"    [!] Error querying crt.sh: {e}")
            return []

    def query_crtsh_identity(self, identity, days=30):
        """Query crt.sh for certificates by identity/organization."""
        url = "https://crt.sh/"
        params = {
            'Identity': identity,
            'output': 'json',
            'iCAID': '-1',
            'iCqlF': 'false',
            'q': '',
        }

        try:
            resp = requests.get(url, params=params, timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                # Filter by date
                cutoff = datetime.now() - timedelta(days=days)
                recent = [
                    entry for entry in data 
                    if entry.get('entry_timestamp') and 
                    datetime.strptime(entry['entry_timestamp'], '%Y-%m-%dT%H:%M:%S.%f') > cutoff
                ]
                return recent
            return []
        except Exception as e:
            print(f"    [!] Error: {e}")
            return []

    def analyze_domain(self, domain, brand='unknown'):
        """Analyze a domain for suspicious characteristics."""
        score = 0
        reasons = []
        domain_lower = domain.lower()

        # Check for suspicious TLD
        for tld in SUSPICIOUS_TLDS:
            if domain_lower.endswith(tld):
                score += 2
                reasons.append(f'suspicious_tld:{tld}')

        # Check for suspicious keywords in domain
        for kw in SUSPICIOUS_KEYWORDS:
            if kw in domain_lower:
                score += 1
                reasons.append(f'suspicious_keyword:{kw}')

        # Check for brand impersonation patterns
        # e.g., bkash-secure-login.tk
        if brand != 'unknown':
            brand_patterns = [
                rf'{brand}[-_](?:login|secure|verify|update|confirm)',
                rf'(?:login|secure|verify|update)[-_]{brand}',
                rf'{brand}\d+',
            ]
            for pattern in brand_patterns:
                if re.search(pattern, domain_lower):
                    score += 3
                    reasons.append(f'brand_impersonation_pattern:{pattern}')

        # Check for typosquatting (character substitution)
        # e.g., bk4sh, bakash, bkush
        typosquats = self._check_typosquatting(domain_lower, brand)
        if typosquats:
            score += 4
            reasons.extend([f'typosquatting:{t}' for t in typosquats])

        # Check for excessive length
        if len(domain) > 40:
            score += 1
            reasons.append('long_domain')

        # Check for excessive subdomains
        if domain.count('.') > 3:
            score += 1
            reasons.append('many_subdomains')

        return {
            'domain': domain,
            'brand': brand,
            'risk_score': score,
            'risk_reasons': reasons,
            'is_suspicious': score >= 3,
        }

    def _check_typosquatting(self, domain, brand):
        """Check for potential typosquatting of brand names."""
        if brand == 'unknown':
            return []

        brand_lower = brand.lower()
        # Simple edit distance check
        if brand_lower not in domain:
            # Check if a similar string exists
            similar = re.search(rf'b{brand_lower[1:]}|{brand_lower[:-1]}[a-z]|{brand_lower[0]}[a-z]{{len(brand_lower)-1}}', domain)
            if similar:
                return [similar.group()]
        return []

    def monitor_brand(self, brand_name, keywords, days=30):
        """Monitor certificate transparency for a specific brand."""
        print(f"[+] Monitoring brand: {brand_name}")
        all_entries = []

        for keyword in keywords:
            print(f"    -> Querying keyword: {keyword}")
            entries = self.query_crtsh(keyword, subdomains=True)
            print(f"       Found {len(entries)} certificate entries")
            all_entries.extend(entries)
            time.sleep(1)  # Rate limiting

        # Analyze unique domains
        domains = defaultdict(list)
        for entry in all_entries:
            name = entry.get('name_value', entry.get('common_name', ''))
            for domain in name.split('\n'):
                domain = domain.strip().lower()
                if domain and '*' not in domain:
                    domains[domain].append(entry)

        print(f"    -> {len(domains)} unique domains found")

        # Risk analysis
        results = []
        for domain, entries in domains.items():
            analysis = self.analyze_domain(domain, brand=brand_name)
            analysis['cert_entries'] = len(entries)
            analysis['first_seen'] = min(
                (e.get('entry_timestamp', '') for e in entries if e.get('entry_timestamp')),
                default=''
            )
            analysis['issuer_name'] = entries[0].get('issuer_name', '') if entries else ''
            results.append(analysis)

        # Sort by risk score
        results.sort(key=lambda x: x['risk_score'], reverse=True)

        # Flag suspicious
        suspicious = [r for r in results if r['is_suspicious']]
        self.suspicious_domains.extend(suspicious)

        print(f"    -> {len(suspicious)} flagged as suspicious")
        return results

    def monitor_all_brands(self, days=30):
        """Monitor all Bangladesh MFS brands."""
        all_results = {}

        for brand, keywords in BD_MFS_BRANDS.items():
            results = self.monitor_brand(brand, keywords, days=days)
            all_results[brand] = results
            time.sleep(2)  # Rate limiting between brands

        return all_results

    def save_results(self, results, prefix="ct_monitor"):
        """Save monitoring results."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        # All results JSON
        json_path = os.path.join(self.raw_dir, f"{prefix}_{timestamp}.json")
        with open(json_path, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"[+] Saved all results: {json_path}")

        # Suspicious only
        if self.suspicious_domains:
            suspicious_path = os.path.join(self.alerts_dir, f"suspicious_{timestamp}.csv")
            with open(suspicious_path, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=['domain', 'brand', 'risk_score', 'risk_reasons', 'cert_entries', 'first_seen', 'issuer_name'])
                writer.writeheader()
                for d in self.suspicious_domains:
                    row = d.copy()
                    row['risk_reasons'] = '|'.join(row['risk_reasons'])
                    writer.writerow(row)
            print(f"[+] Saved suspicious domains: {suspicious_path}")

        # Summary report
        report = {
            'generated_at': datetime.now().isoformat(),
            'brands_monitored': list(results.keys()),
            'total_domains': sum(len(v) for v in results.values()),
            'suspicious_domains': len(self.suspicious_domains),
            'suspicious_by_brand': defaultdict(int),
            'top_risk_domains': [
                {'domain': d['domain'], 'score': d['risk_score'], 'reasons': d['risk_reasons']}
                for d in sorted(self.suspicious_domains, key=lambda x: x['risk_score'], reverse=True)[:20]
            ]
        }

        for d in self.suspicious_domains:
            report['suspicious_by_brand'][d['brand']] += 1

        report_path = os.path.join(self.alerts_dir, f"report_{timestamp}.json")
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        # Print summary
        print("\n" + "="*60)
        print("CERTIFICATE TRANSPARENCY MONITORING REPORT")
        print("="*60)
        print(f"Brands monitored:       {report['brands_monitored']}")
        print(f"Total domains found:    {report['total_domains']}")
        print(f"Suspicious flagged:     {report['suspicious_domains']}")
        print(f"By brand:               {dict(report['suspicious_by_brand'])}")
        print(f"\nTop suspicious domains:")
        for d in report['top_risk_domains'][:10]:
            print(f"  [{d['score']}] {d['domain']} - {d['reasons']}")
        print("="*60)

        return report


def main():
    parser = argparse.ArgumentParser(description="Certificate Transparency Log Monitor for BD MFS")
    parser.add_argument("--output", default="./ct_monitor", help="Output directory")
    parser.add_argument("--brands", default="all", help="Comma-separated brands or 'all'")
    parser.add_argument("--days", type=int, default=30, help="Days to look back")
    parser.add_argument("--stream", action="store_true", help="Enable CertStream real-time monitoring")
    parser.add_argument("--score-threshold", type=int, default=3, help="Suspicious score threshold")

    args = parser.parse_args()

    monitor = CTLogMonitor(output_dir=args.output)

    if args.stream:
        print("[!] CertStream real-time monitoring requires: pip install certstream")
        print("    Run: python -c 'import certstream; certstream.listen_for_events(callback)'")
        return

    brands = list(BD_MFS_BRANDS.keys()) if args.brands == 'all' else args.brands.split(',')

    all_results = {}
    for brand in brands:
        if brand in BD_MFS_BRANDS:
            results = monitor.monitor_brand(brand, BD_MFS_BRANDS[brand], days=args.days)
            all_results[brand] = results
        else:
            print(f"[!] Unknown brand: {brand}")

    monitor.save_results(all_results)
    print("\n[*] Monitoring complete!")


if __name__ == "__main__":
    main()
