#!/usr/bin/env python3
"""
Helper to download the Mendeley Financial Scams Detection Dataset
Options: manual URL, Selenium automation, or API token

Usage:
    python download_mendeley_dataset.py --manual
    python download_mendeley_dataset.py --email YOUR_EMAIL --password YOUR_PASSWORD
"""

import argparse
import os
import sys
import time

import requests

DATASET_ID = "znsk27yk3h"
VERSION = "1"
FILENAME = "Financial scams detection dataset.csv"
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "financial_scams_detection_dataset.csv")

MENDELEY_URL = f"https://data.mendeley.com/datasets/{DATASET_ID}/{VERSION}"
DOWNLOAD_URL = f"https://data.mendeley.com/v1/datasets/{DATASET_ID}/{VERSION}/files/{FILENAME}/download"


def download_manual():
    """Print instructions for manual download."""
    print("="*60)
    print("MANUAL DOWNLOAD INSTRUCTIONS")
    print("="*60)
    print(f"1. Visit: {MENDELEY_URL}")
    print(f"2. Click the 'Download All' button")
    print(f"3. Extract the CSV file")
    print(f"4. Place it at: {OUTPUT_FILE}")
    print(f"5. Verify: python -c "import pandas as pd; df=pd.read_csv('{OUTPUT_FILE}'); print(len(df), 'rows')"")
    print("="*60)


def download_with_selenium(email, password):
    """Automated download using Selenium (requires Chrome)."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
    except ImportError:
        print("ERROR: Install selenium: pip install selenium")
        sys.exit(1)

    print(f"[+] Opening Mendeley page...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_experimental_option("prefs", {
        "download.default_directory": OUTPUT_DIR,
        "download.prompt_for_download": False
    })

    driver = webdriver.Chrome(options=options)

    try:
        # Login
        driver.get("https://data.mendeley.com/user/login")
        time.sleep(2)

        driver.find_element(By.NAME, "email").send_keys(email)
        driver.find_element(By.NAME, "password").send_keys(password)
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()

        time.sleep(3)

        # Navigate to dataset
        driver.get(MENDELEY_URL)
        time.sleep(3)

        # Find download button
        download_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download')]"))
        )
        download_btn.click()

        time.sleep(10)  # Wait for download
        print(f"[✓] Download complete. Check: {OUTPUT_DIR}")

    finally:
        driver.quit()


def download_with_api_token(token):
    """Download using Mendeley API token."""
    headers = {"Authorization": f"Bearer {token}"}

    print(f"[+] Downloading with API token...")
    resp = requests.get(DOWNLOAD_URL, headers=headers, stream=True)

    if resp.status_code == 200:
        with open(OUTPUT_FILE, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
        print(f"[✓] Downloaded: {OUTPUT_FILE}")
        print(f"    Size: {os.path.getsize(OUTPUT_FILE)} bytes")
    else:
        print(f"[!] Failed: HTTP {resp.status_code}")
        print(f"    {resp.text[:200]}")


def verify_download():
    """Verify the downloaded file."""
    import pandas as pd

    if not os.path.exists(OUTPUT_FILE):
        print(f"[!] File not found: {OUTPUT_FILE}")
        return False

    try:
        df = pd.read_csv(OUTPUT_FILE)
        print("\n" + "="*60)
        print("DATASET VERIFICATION")
        print("="*60)
        print(f"File:         {OUTPUT_FILE}")
        print(f"Rows:         {len(df)}")
        print(f"Columns:      {list(df.columns)}")
        print(f"Size:         {os.path.getsize(OUTPUT_FILE)} bytes")

        # Detect label column
        label_cols = [c for c in df.columns if any(k in c.lower() for k in ['label', 'class', 'type', 'scam', 'ham'])]
        if label_cols:
            print(f"\nLabel column: {label_cols[0]}")
            print(f"Label distribution:")
            print(df[label_cols[0]].value_counts())

        print("="*60)
        return True

    except Exception as e:
        print(f"[!] Error reading file: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Download Mendeley Financial Scams Dataset")
    parser.add_argument("--manual", action="store_true", help="Show manual download instructions")
    parser.add_argument("--email", help="Mendeley email (for Selenium)")
    parser.add_argument("--password", help="Mendeley password")
    parser.add_argument("--token", help="Mendeley API token")
    parser.add_argument("--verify", action="store_true", help="Verify downloaded file")

    args = parser.parse_args()

    if args.manual:
        download_manual()
    elif args.email and args.password:
        download_with_selenium(args.email, args.password)
    elif args.token:
        download_with_api_token(args.token)
    elif args.verify:
        verify_download()
    else:
        # Default: try direct download first, then show manual instructions
        print("[+] Attempting direct download...")
        print("[!] Mendeley requires authentication. Showing manual instructions:")
        print()
        download_manual()


if __name__ == "__main__":
    main()
