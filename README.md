# MFS Scam Research - Data Collection Toolkit
## Measuring Mobile Financial Services (MFS) Scam Ecosystems in Bangladesh

**Target Venues:** NDSS | IEEE S&P | USENIX Security | ACM CCS

---

## Quick Start

```bash
# 1. Install all dependencies
pip install google-play-scraper pandas numpy requests dnspython
pip install presidio-analyzer presidio-anonymizer  # optional, for PII detection

# 2. Download the Mendeley baseline dataset
python download_mendeley_dataset.py

# 3. Run the data processing pipeline on it
python data_pipeline/process_dataset.py --input financial_scams_detection_dataset.csv --output clean_dataset.csv --profile table1_stats.json

# 4. Start collecting app reviews
python stream_e_app_reviews/app_review_scraper.py --all --count 5000 --output ./app_reviews

# 5. Start monitoring phishing URLs
python stream_c_phishing_urls/phishing_pipeline.py --refresh-all --enrich

# 6. Generate survey form
python survey_form/survey_toolkit.py --generate --output ./survey

# 7. Launch annotation interface
python annotation_interface/annotation_tool.py --setup --dataset clean_dataset.csv --output ./annotation
```

---

## Directory Structure

```
mfs_scam_research/
|-- stream_a_datasets/              # Stream A: Baseline dataset
|   |-- download_mendeley_dataset.py # Helper to download from Mendeley
|   |-- financial_scams_detection_dataset.csv  # Baseline dataset (after download)
|   |-- table1_stats.json            # Dataset profile for paper Table 1
|
|-- stream_e_app_reviews/           # Stream E: App review mining
|   |-- app_review_scraper.py       # Google Play scraper for bKash/Nagad/Rocket/Upay
|   |-- fraud_keywords.json         # English + Bangla fraud keyword list
|   |-- mfs_app_reviews.json        # Collected reviews (after running)
|   |-- mfs_app_reviews_fraud_only.json
|   |-- mfs_app_reviews_statistics.json
|
|-- stream_c_phishing_urls/         # Stream C: Phishing URL collection
|   |-- phishing_pipeline.py        # PhishTank + OpenPhish + URLhaus pipeline
|   |-- phishing_urls.json          # Enriched phishing URL dataset
|   |-- phishing_urls.csv           # CSV version
|   |-- reports/                    # Infrastructure analysis reports
|
|-- data_pipeline/                  # Data processing pipeline
|   |-- process_dataset.py          # De-identification + feature extraction
|   |-- deidentification_rules.json # BD-specific PII patterns
|   |-- feature_schema.json         # Feature definitions
|
|-- survey_form/                    # User survey (Phase 7)
|   |-- survey_toolkit.py           # Form generator + data processor
|   |-- survey_form.html            # Generated HTML survey form
|   |-- survey_schema.json          # JSON schema for import
|
|-- annotation_interface/           # Taxonomy annotation tool
|   |-- annotation_tool.py          # 7-category codebook + IAA calculator
|   |-- annotation_interface.html   # Web-based annotation UI
|   |-- taxonomy_codebook.json      # Full codebook with examples
|
|-- infrastructure_monitoring/      # Certificate Transparency monitoring
|   |-- ct_monitor.py               # crt.sh scraper for BD brand domains
|   |-- alerts/                     # Suspicious domain alerts

|-- deliverables/                   # Final packaged deliverables
|   |-- README.md                   # This file
|   |-- setup.sh                    # One-command setup script
```

---

## Stream A: Mendeley Baseline Dataset

### About the Dataset
- **Source:** Mendeley Data, DOI: 10.17632/znsk27yk3h.1
- **Authors:** Al Rafi Ahmed, Gazi Faizul Islam
- **Institution:** International University of Business Agriculture and Technology
- **License:** CC BY 4.0
- **Content:** Labeled scam/ham messages in English and Bangla covering fake bKash/Nagad offers, lottery, loan scams, OTP fraud, banking phishing

### How to Download

**Option 1: Manual Download**
1. Visit: https://data.mendeley.com/datasets/znsk27yk3h/1
2. Click "Download All" button
3. Place the CSV file in `stream_a_datasets/`

**Option 2: Automated Download (requires account)**
```bash
python download_mendeley_dataset.py --email YOUR_EMAIL --password YOUR_PASSWORD
```

**Option 3: Via API token**
```bash
export MENDELEY_TOKEN="your_api_token"
python download_mendeley_dataset.py --token
```

### Processing the Dataset

```bash
python data_pipeline/process_dataset.py \
    --input stream_a_datasets/financial_scams_detection_dataset.csv \
    --output stream_a_datasets/clean_dataset.csv \
    --profile stream_a_datasets/table1_stats.json
```

This will:
- De-identify PII (phone numbers, NIDs, account numbers)
- Extract 30+ textual and structural features
- Generate Table 1 statistics for your paper

---

## Stream E: App Review Scraper

### What It Collects
User reviews from Google Play for bKash, Nagad, Rocket, Upay, and SureCash apps, filtered for fraud-related keywords.

### Supported Apps
| App | Package Name | Status |
|-----|-------------|--------|
| bKash | `com.bKash.customerapp` | Active |
| Nagad | `com.kamatham.nagad` | Active |
| Rocket | `com.dbbl.mbs` | Active |
| Upay | `com.upay` | Active |
| SureCash | `com.progotisystems.android.surecash` | Active |

### Usage

```bash
# Scrape all apps (5000 reviews each)
python stream_e_app_reviews/app_review_scraper.py --all --count 5000

# Scrape specific app
python stream_e_app_reviews/app_review_scraper.py --app bkash --count 10000

# Output files:
# - app_reviews/mfs_app_reviews.json         (all reviews)
# - app_reviews/mfs_app_reviews.csv          (CSV format)
# - app_reviews/mfs_app_reviews_fraud_only.json  (fraud-keyword matches only)
# - app_reviews/mfs_app_reviews_statistics.json  (profiling stats)
```

### Fraud Keywords
The scraper matches against 40+ English and Bangla fraud keywords including: fraud, scam, OTP, hacked, stolen, প্রতারণা, টাকা চলে গেছে, ফেক, হ্যাক, etc.

---

## Stream C: Phishing URL Pipeline

### Data Sources
| Source | Type | Access |
|--------|------|--------|
| PhishTank | Community-verified phishing URLs | Open API (registration required for full) |
| OpenPhish | Automated phishing feed | Free tier available |
| URLhaus | Malware/phishing URL database | Open API |
| CIRT Bangladesh | Government advisories | Web scraping |

### Brand Keywords Monitored
- bKash, Nagad, Rocket, DBBL, BRAC Bank, SureCash, Upay
- Generic: Bangladesh, BD, taka, mobile banking, MFS

### Usage

```bash
# Fetch and enrich all sources
python stream_c_phishing_urls/phishing_pipeline.py --refresh-all --enrich

# Generate report from existing data
python stream_c_phishing_urls/phishing_pipeline.py --status-report

# Customize delay between enrichment requests (default: 1 second)
python stream_c_phishing_urls/phishing_pipeline.py --refresh-all --enrich --delay 2
```

### Enrichment Data
Each URL is enriched with:
- Hosting ASN and country
- Domain age and registrar
- SSL certificate presence
- URL shortener detection
- Infrastructure clustering features

---

## Data Processing Pipeline

### De-identification

**Regex-based (always available):**
- Bangladesh mobile numbers (+8801XXXXXXXXX, 01XXXXXXXXX)
- National ID numbers (10/13/17 digits)
- Bank account numbers (9-16 digits)
- Credit/debit card numbers
- Email addresses
- PIN/OTP patterns

**Presidio-enhanced (optional):**
- Person names
- Location entities
- Organization names
- Custom Bangladesh-specific entities

### Features Extracted

| Category | Features |
|----------|----------|
| Basic Stats | char_count, word_count, sentence_count, avg_word_length |
| Language | contains_bangla, bangla_ratio, is_code_mixed |
| URL | has_url, url_count, uses_url_shortener |
| Phone | has_phone, phone_count |
| Content | urgency_word_count, scam_indicator_count, action_word_count |
| Punctuation | exclamation_count, all_caps_words, digit_ratio |
| MFS-specific | mentions_bkash, mentions_nagad, mentions_otp, mentions_pin |

---

## Survey Form (Phase 7)

### Sections
| Section | Content | Questions |
|---------|---------|-----------|
| A | Demographics (age, gender, education, location, income) | 6 |
| B | MFS Usage Patterns | 4 |
| C | Scam Exposure | 5 |
| D | Digital Literacy (5-point Likert) | 5 |
| E | Trust and Awareness | 3 |
| F | Message Classification Vignette | 5 |

### Generated Scores
- **Digital Literacy Score:** Average of D1-D5 (1-5 scale, higher = more literate)
- **Susceptibility Score:** % of vignettes incorrectly classified (higher = more susceptible)

### Usage

```bash
# Generate HTML form + JSON schema
python survey_form/survey_toolkit.py --generate --output ./survey

# Process collected responses
python survey_form/survey_toolkit.py --process responses.csv --report survey_report.json
```

---

## Annotation Interface

### 7-Category Taxonomy Codebook

| ID | Category | Key Indicators |
|----|----------|---------------|
| 1 | Account Compromise | suspended, blocked, OTP, PIN, unauthorized |
| 2 | Fake Promotional Offer | cashback, bonus, offer, free, activate |
| 3 | Lottery / Prize Scam | won, winner, lottery, prize, claim |
| 4 | Loan / Job Scam | loan, job, processing fee, registration |
| 5 | Impersonation | emergency, uncle, boss, help, urgent |
| 6 | Phishing Link | http, click, link, .tk, .xyz, verify |
| 7 | Legitimate (Ham) | successful, received, balance, TxID |

### Inter-Annotator Agreement

```bash
# After two annotators complete labeling:
python annotation_interface/annotation_tool.py \
    --agreement \
    --annotations annotator1.csv annotator2.csv \
    --report iaa_report.json
```

Computes:
- Overall agreement percentage
- Cohen's Kappa
- Category-level agreement breakdown
- Disagreement cases for adjudication

---

## Infrastructure Monitoring

### Certificate Transparency Log Monitoring

```bash
# Monitor all BD MFS brands for suspicious certificate issuance
python infrastructure_monitoring/ct_monitor.py --brands all --days 30

# Monitor specific brand
python infrastructure_monitoring/ct_monitor.py --brands bkash --days 7
```

**Detection capabilities:**
- Typosquatting detection (bKash -> bk4sh, bakash)
- Brand impersonation patterns (bkash-secure-login.tk)
- Suspicious TLD monitoring (.tk, .ml, .xyz)
- Suspicious keyword detection (login, verify, secure + brand name)

---

## Installation

### Requirements
- Python 3.8+
- 4GB RAM minimum
- Internet connection for API calls

### One-Command Setup
```bash
chmod +x setup.sh
./setup.sh
```

### Manual Setup
```bash
# Core dependencies
pip install google-play-scraper pandas numpy requests dnspython

# Optional: PII detection (recommended)
pip install presidio-analyzer presidio-anonymizer

# Optional: Certificate monitoring
pip install certstream

# Optional: Statistical analysis
pip install scipy statsmodels scikit-learn
```

---

## Ethical Considerations

1. **Never collect real transaction data, account numbers, or NIDs**
2. **Scam messages only with explicit informed consent**
3. **Social media scraping limited to publicly visible content**
4. **Do not impersonate users or join private groups under false pretenses**
5. **Report findings to BGD e-GOV CIRT before publication**
6. **All automated tools respect rate limits and ToS**

---

## Troubleshooting

### Common Issues

**Issue:** `ModuleNotFoundError: No module named 'google_play_scraper'`
**Fix:** `pip install google-play-scraper`

**Issue:** PhishTank API returns 403
**Fix:** Register at phishtank.org and use API key

**Issue:** Google Play scraper returns empty results
**Fix:** The target app may not be available in your region. Try with `--country bd`

**Issue:** Certificate monitoring rate limited
**Fix:** Increase delay with `--delay 5`

---

## Citation

If you use these tools in your research, cite:

```bibtex
@dataset{ahmed2024financial,
  title={Financial scams detection dataset},
  author={Ahmed, Al Rafi and Islam, Gazi Faizul},
  year={2024},
  publisher={Mendeley Data},
  doi={10.17632/znsk27yk3h.1}
}
```

---

## Timeline

| Month | Activity |
|-------|----------|
| 3 | Download & profile Mendeley dataset; Launch app review collection |
| 4 | Set up PhishTank/OpenPhish pipeline; Start CT monitoring |
| 5 | Complete app reviews; Start social media discovery |
| 6 | Complete phishing URL collection; Launch survey form |
| 7 | Annotation with inter-annotator agreement |
| 8 | Dataset freeze; Begin measurement analysis |

---

**Last Updated:** May 2026
**For questions:** Contact your research supervisor or open an issue

---

## Stream D: Social Media & Underground Economy

### NEW: Discovered Real Fraud Infrastructure

During setup, we discovered **active Telegram channels** openly processing bKash/Nagad payments for cross-border fraud schemes, plus **$1.9 billion in MFS fraud losses** from news investigations.

See full details: `stream_d_social_media/DISCOVERED_EVIDENCE.md`

### Telegram Public Channel Scraper
```bash
# Scrape discovered channels
python stream_d_social_media/telegram_scraper.py --all-known --output ./telegram_data

# Target list: stream_d_social_media/telegram_targets.txt
```

**Discovered Channels:**
| Channel | Description | Risk Indicators |
|---------|-------------|-----------------|
| @LGPaymentgateway | Payment gateway (1.09K subscribers) | Handles bKash/Nagad, warns about cheaters |
| @ag4566 | OKEXPAY - overseas payment | 80% success rate, D0 settlement, gaming clients |

### Facebook Public Page Scraper
```bash
# With Selenium (recommended)
python stream_d_social_media/facebook_scraper.py --page PAGE_NAME --selenium

# Search for pages
python stream_d_social_media/facebook_scraper.py --search-terms "bKash offer,Nagad bonus" --discover
```

### Key Statistics for Your Paper
- **Tk 21,000 crore** (~$1.9B USD) vanished in MFS fraud (Observer BD, May 2026)
- **6.3%** of individual MFS users victimized
- **17%** of MFS agents victimized  
- **51,251 SIM cards** recovered from single fraud syndicate
- Multiple Chinese nationals arrested for Telegram-based bKash/Nagad fraud

