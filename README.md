# MFS Scam Research - Data Collection Toolkit
## Measuring Mobile Financial Services (MFS) Scam Ecosystems in Bangladesh

**Target Venues:** NDSS | IEEE S&P | USENIX Security | ACM CCS

---

## Quick Start

```bash
# 1. Install all dependencies
pip install google-play-scraper pandas numpy requests dnspython
pip install presidio-analyzer presidio-anonymizer  # optional, for PII detection

# 2. Download the Mendeley baseline datasets (see Stream A below)

# 3. Run the data processing pipeline on Dataset 1
python data_pipeline/process_dataset.py \
    --input stream_a_datasets/financial_scams_detection_dataset.csv \
    --output stream_a_datasets/clean_dataset_1.csv \
    --profile stream_a_datasets/table1_stats_1.json

# 4. Run the data processing pipeline on Dataset 2 (BanglaBarta)
python data_pipeline/process_dataset.py \
    --input stream_a_datasets/banglabarta_dataset.csv \
    --output stream_a_datasets/clean_dataset_2.csv \
    --profile stream_a_datasets/table1_stats_2.json

# 5. Start collecting app reviews
python stream_e_app_reviews/app_review_scraper.py --all --count 5000 --output ./app_reviews

# 6. Start monitoring phishing URLs
python stream_c_phishing_urls/phishing_pipeline.py --refresh-all --enrich

# 7. Generate survey form
python survey_form/survey_toolkit.py --generate --output ./survey

# 8. Prepare annotation dataset (600 messages, 2 annotator sheets)
python annotation_package/prepare_annotation_set.py
```

---

## Directory Structure

```
mfs_scam_research/
|-- stream_a_datasets/              # Stream A: Baseline datasets
|   |-- download_mendeley_dataset.py
|   |-- financial_scams_detection_dataset.csv   # Dataset 1 (523 messages)
|   |-- banglabarta_dataset.csv                 # Dataset 2 (2,772 messages)
|   |-- clean_dataset_1.csv                     # PII-redacted Dataset 1
|   |-- clean_dataset_2.csv                     # PII-redacted Dataset 2
|   |-- table1_stats_1.json                     # Table 1 stats for paper
|   |-- table1_stats_2.json
|
|-- stream_e_app_reviews/           # Stream E: App review mining
|   |-- app_review_scraper.py
|
|-- stream_c_phishing_urls/         # Stream C: Phishing URL collection
|   |-- phishing_pipeline.py
|
|-- stream_d_social_media/          # Stream D: Telegram / social media
|   |-- telegram_scraper.py
|   |-- telegram_targets.txt
|
|-- data_pipeline/                  # Data processing pipeline
|   |-- process_dataset.py
|
|-- annotation_package/             # Annotation task
|   |-- prepare_annotation_set.py   # Generates 600-msg dataset + annotator sheets
|   |-- annotation_batch.csv        # 600 messages for annotation
|   |-- annotation_sheet_A1.xlsx    # Annotator 1 spreadsheet
|   |-- annotation_sheet_A2.xlsx    # Annotator 2 spreadsheet
|   |-- annotation_guidelines.docx  # Codebook with examples
|   |-- kappa_calculator.py         # Cohen's Kappa after annotation
|   |-- recruitment_email.txt       # Email template for recruiting annotators
|
|-- survey_form/                    # User survey
|   |-- survey_toolkit.py
|   |-- survey_form.html
|   |-- survey_schema.json
|
|-- irb/                            # IRB / ethics package (LSU)
|   |-- lsu_irb_application.docx
|   |-- lsu_informed_consent.docx
|   |-- lsu_data_management_plan.docx
|
|-- infrastructure_monitoring/      # Certificate Transparency monitoring
|   |-- ct_monitor.py
|
|-- deliverables/
|   |-- setup.sh
```

---

## Stream A: Mendeley Baseline Datasets

This research uses **two** publicly available Mendeley datasets as primary training and evaluation corpora.

---

### Dataset 1 — Financial Scams Detection Dataset

| Field | Details |
|-------|---------|
| **Source** | Mendeley Data |
| **DOI** | [10.17632/znsk27yk3h.1](https://data.mendeley.com/datasets/znsk27yk3h/1) |
| **Direct Link** | https://data.mendeley.com/datasets/znsk27yk3h/1 |
| **Authors** | Al Rafi Ahmed, Gazi Faizul Islam |
| **Institution** | International University of Business Agriculture and Technology, Bangladesh |
| **License** | CC BY 4.0 |
| **Size** | 523 messages |
| **Labels** | `scam` (310), `ham` (213) |
| **Language** | English + Bangla (code-mixed) |
| **Content** | Labeled scam/ham SMS covering fake bKash/Nagad offers, lottery, loan scams, OTP fraud, banking phishing |

**How to Download — Dataset 1:**

Option 1: Manual
1. Visit: https://data.mendeley.com/datasets/znsk27yk3h/1
2. Click **"Download All"**
3. Rename file to `financial_scams_detection_dataset.csv`
4. Place in `stream_a_datasets/`

Option 2: Direct file URL
```bash
wget -O stream_a_datasets/financial_scams_detection_dataset.csv \
  "https://data.mendeley.com/public-files/datasets/znsk27yk3h/files/[file-id]/file_downloaded"
```

---

### Dataset 2 — BanglaBarta SMS Spam/Smishing Dataset

| Field | Details |
|-------|---------|
| **Source** | Mendeley Data |
| **DOI** | [10.17632/jfkfbw3gzh/2](https://data.mendeley.com/datasets/jfkfbw3gzh/2) |
| **Direct Link** | https://data.mendeley.com/datasets/jfkfbw3gzh/2 |
| **License** | CC BY 4.0 |
| **Size** | 2,772 messages |
| **Labels** | `smish` (924), `promo` (924), `normal` (924) — perfectly balanced |
| **Language** | Bangla-dominant (99.4% contain Bangla), heavily code-mixed (67.9%) |
| **Content** | Bangla SMS dataset covering smishing attacks, promotional spam, and legitimate messages. Ideal for Bangla-language scam detection. |

**How to Download — Dataset 2:**

Option 1: Manual
1. Visit: https://data.mendeley.com/datasets/jfkfbw3gzh/2
2. Click **"Download All"**
3. Rename file to `banglabarta_dataset.csv`
4. Place in `stream_a_datasets/`

Option 2: Direct file URL
```bash
wget -O stream_a_datasets/banglabarta_dataset.csv \
  "https://data.mendeley.com/public-files/datasets/jfkfbw3gzh/files/[file-id]/file_downloaded"
```

---

### Processing Both Datasets

```bash
# Dataset 1 — Financial Scams
python data_pipeline/process_dataset.py \
    --input stream_a_datasets/financial_scams_detection_dataset.csv \
    --output stream_a_datasets/clean_dataset_1.csv \
    --profile stream_a_datasets/table1_stats_1.json

# Dataset 2 — BanglaBarta
python data_pipeline/process_dataset.py \
    --input stream_a_datasets/banglabarta_dataset.csv \
    --output stream_a_datasets/clean_dataset_2.csv \
    --profile stream_a_datasets/table1_stats_2.json
```

Both pipelines will:
- De-identify PII (phone numbers, NIDs, bank account numbers, card numbers)
- Extract 30+ textual and structural features
- Generate Table 1 statistics for your paper

### Table 1 Summary (Actual Collected Data)

| | Dataset 1 (Financial Scams) | Dataset 2 (BanglaBarta) |
|---|---|---|
| Total messages | 523 | 2,772 |
| Labels | scam: 310, ham: 213 | smish: 924, promo: 924, normal: 924 |
| Bangla content | 101 (19.3%) | 2,754 (99.4%) |
| Code-mixed | 34 (6.5%) | 1,882 (67.9%) |
| Avg message length | 66.8 chars | 68.3 chars |
| Messages with PII | 155 (29.6%) | 1,839 (66.3%) |
| PII instances redacted | 184 | 3,664 |

---

## Stream E: App Review Scraper

### What It Collects
User reviews from Google Play for bKash, Nagad, and Rocket apps, filtered for fraud-related keywords.

### Supported Apps
| App | Package Name | Status |
|-----|-------------|--------|
| bKash | `com.bKash.customerapp` | ✅ Verified |
| Nagad | `com.konasl.nagad` | ✅ Verified |
| Rocket | `com.dbbl.mbs.apps.main` | ✅ Verified |

### Usage

```bash
python stream_e_app_reviews/app_review_scraper.py --all --count 5000
```

### Actual Results (May 2026)
- **Total reviews collected:** 15,300 (5,100 per app)
- **Fraud-flagged reviews:** 243 (1.6%)
- **Languages:** English + Bangla

---

## Stream C: Phishing URL Pipeline

### Data Sources
| Source | Type | Access |
|--------|------|--------|
| PhishTank | Community-verified phishing URLs | Open API |
| OpenPhish | Automated phishing feed | Free tier |
| URLhaus | Malware/phishing URL database | Open API |

### Usage

```bash
python stream_c_phishing_urls/phishing_pipeline.py --refresh-all --enrich
```

### Actual Results (May 2026)
- **Live BD-brand phishing URLs:** 3 (from OpenPhish)
- **URLhaus:** Requires authentication (401)
- **PhishTank:** Rate limited (429)

---

## Stream D: Social Media & Underground Economy

### Discovered Active Fraud Infrastructure

During collection, active Telegram channels openly processing bKash/Nagad payments for cross-border fraud schemes were discovered.

```bash
python stream_d_social_media/telegram_scraper.py --all-known --output ./telegram_data
```

### Actual Results (May 2026)
| Channel | Posts Collected | Fraud Posts | bKash Mentions |
|---------|----------------|-------------|----------------|
| @LGPaymentgateway | 1,587 | 395 | 201 |
| @ag4566 | 757 | 164 | 143 |
| **Total** | **2,344** | **559** | **344** |

### Key Statistics
- **Tk 21,000 crore** (~$1.9B USD) in MFS fraud losses (Observer BD, May 2026)
- **6.3%** of individual MFS users victimized
- **17%** of MFS agents victimized
- **51,251 SIM cards** recovered from single fraud syndicate

---

## Annotation Package

### Overview
600 messages sampled from collected data, labelled by 2 independent native Bangla-speaking annotators using a 7-category taxonomy. Target inter-annotator agreement: Cohen's Kappa ≥ 0.80.

### 7-Category Taxonomy

| Code | Category | Key Indicators |
|------|----------|----------------|
| S1 | Account Compromise | OTP theft, hacking, unauthorized access, PIN stolen |
| S2 | Fake Promotion | Fake cashback, fake bonus, fraudulent offer |
| S3 | Lottery / Prize | Lottery won, prize claim, lucky draw scam |
| S4 | Loan / Job Scam | Fake loan, fake job, advance fee fraud |
| S5 | Impersonation | Fake agent, fake customer care, fake MFS staff |
| S6 | Phishing Link | Fake URL, clone app, malware link |
| L0 | Ham (Legitimate) | Genuine review, real complaint, normal transaction |

### Annotation Batch Statistics (600 messages)
| Source | Count |
|--------|-------|
| BanglaBarta | 381 (63.5%) |
| Mendeley Financial Scams | 185 (30.8%) |
| App Reviews (fraud-flagged) | 34 (5.7%) |

### Running the Annotation

```bash
# Step 1: Generate annotator sheets (run once)
pip install openpyxl --break-system-packages
python annotation_package/prepare_annotation_set.py

# Step 2: Distribute sheets to annotators
# annotation_package/annotation_sheet_A1.xlsx → Annotator 1
# annotation_package/annotation_sheet_A2.xlsx → Annotator 2
# annotation_package/annotation_guidelines.docx → both annotators

# Step 3: After both annotators finish, compute Kappa
pip install scikit-learn --break-system-packages
python annotation_package/kappa_calculator.py
```

---

## IRB / Ethics (LSU)

This study was submitted to the Louisiana State University Institutional Review Board under Exempt Category 2 (45 CFR 46.104(d)(2)).

| Document | Location |
|----------|----------|
| IRB Application | `irb/lsu_irb_application.docx` |
| Informed Consent Form | `irb/lsu_informed_consent.docx` |
| Data Management Plan | `irb/lsu_data_management_plan.docx` |

Submit via iRIS: https://lsu.edu/research/ors/compliance/irb

---

## Data Processing Pipeline

### De-identification
- Bangladesh mobile numbers (01XXXXXXXXX)
- National ID numbers (10/13/17 digits)
- Bank account numbers
- Credit/debit card numbers
- Person names, locations (via Microsoft Presidio)

### Features Extracted

| Category | Features |
|----------|----------|
| Basic Stats | char_count, word_count, avg_word_length |
| Language | contains_bangla, bangla_ratio, is_code_mixed |
| URL | has_url, url_count, uses_url_shortener |
| Phone | has_phone, phone_count |
| Content | urgency_word_count, scam_indicator_count |
| MFS-specific | mentions_bkash, mentions_nagad, mentions_otp, mentions_pin |

---

## Installation

### Requirements
- Python 3.8+
- Anaconda (recommended)
- Internet connection for API calls

### Setup
```bash
pip install google-play-scraper pandas numpy requests beautifulsoup4
pip install presidio-analyzer presidio-anonymizer openpyxl scikit-learn
python -m spacy download en_core_web_lg
```

---

## Ethical Considerations

1. All data collected from publicly accessible sources only
2. No authentication bypass or private group scraping
3. Survey participants provide informed consent (LSU IRB approved)
4. All datasets PII-redacted before analysis
5. Phishing URLs treated as indicators only — never activated
6. Findings to be reported to BGD e-GOV CIRT before publication

---

## Citation

```bibtex
@dataset{ahmed2024financial,
  title   = {Financial scams detection dataset},
  author  = {Ahmed, Al Rafi and Islam, Gazi Faizul},
  year    = {2024},
  publisher = {Mendeley Data},
  doi     = {10.17632/znsk27yk3h.1}
}

@dataset{banglabarta2024,
  title   = {BanglaBarta SMS Spam/Smishing Dataset},
  year    = {2024},
  publisher = {Mendeley Data},
  doi     = {10.17632/jfkfbw3gzh/2},
  url     = {https://data.mendeley.com/datasets/jfkfbw3gzh/2}
}
```

---

## Research Timeline

| Phase | Activity | Status |
|-------|----------|--------|
| Data Collection | All 5 streams | ✅ Complete |
| PII Redaction | Both Mendeley datasets | ✅ Complete |
| IRB Package | LSU submission | ✅ Ready |
| Annotation | Recruit annotators, label 600 msgs | 🔄 In Progress |
| Survey | Deploy after IRB approval | ⏳ Pending |
| Model Training | BanglaBERT fine-tuning | ⏳ Pending |
| Paper Writing | USENIX Security target | ⏳ In Progress |

---

**Last Updated:** May 2026
**Contact:** saidur@lsu.edu
**GitHub:** https://github.com/mrahm65/MFS-Scam-Spectrum-Research-Project
