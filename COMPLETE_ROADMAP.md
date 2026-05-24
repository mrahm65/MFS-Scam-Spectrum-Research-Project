# Complete Research Roadmap: MFS Scam Ecosystem Paper
## From Zero to Tier-1 Security Conference Submission

**Target:** NDSS / USENIX Security / IEEE S&P / ACM CCS
**Duration:** 20 weeks (5 months) — aggressive but realistic
**Prerequisite:** You have the 20-file toolkit in `mfs_scam_research/`

---

# PHASE 0: FOUNDATION (Week 1)
## Goal: Everything set up, IRB submitted, first data flowing

---

## Day 1 (Monday)

### Task 1: Environment Setup (2 hours)

```bash
# 1. Create project folder on your machine
mkdir ~/mfs_scam_research && cd ~/mfs_scam_research

# 2. Copy all 20 files from the toolkit here (copy from where you saved them)
# OR if they're in a zip, unzip them

# 3. Create Python virtual environment (CRITICAL — don't use system Python)
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 4. Install all dependencies
pip install google-play-scraper pandas numpy requests beautifulsoup4 lxml dnspython
pip install presidio-analyzer presidio-anonymizer  # optional
pip install selenium webdriver-manager  # for Facebook scraper

# 5. Verify installations
python3 -c "import google_play_scraper, pandas, requests, bs4; print('All OK')"
```

### Task 2: Download Both Mendeley Datasets (1 hour)

**Dataset 1: Financial Scams Detection Dataset**
```
1. Open browser → https://data.mendeley.com/datasets/znsk27yk3h/1
2. Click "Download All" button
3. Extract the ZIP → rename CSV to `financial_scams_detection_dataset.csv`
4. Move to: stream_a_datasets/financial_scams_detection_dataset.csv
```

**Dataset 2: BanglaBarta**
```
1. Open browser → https://data.mendeley.com/datasets/jfkfbw3gzh/2
2. Click "Download All" button  
3. Extract the ZIP → rename to `banglabarta_dataset.csv`
4. Move to: stream_a_datasets/banglabarta_dataset.csv
```

### Task 3: Download TI-Bangladesh Report (15 minutes)
```
https://www.ti-bangladesh.org/images/2025/report/mfs/Executive-Summary-Mobile-Financial-Services-Sector-En.pdf
Save as: stream_a_datasets/ti_bangladesh_mfs_report.pdf
```

**Deliverable by end of Day 1:**
- [ ] Virtual environment working
- [ ] Both datasets downloaded
- [ ] TI report downloaded
- [ ] All files in correct locations

---

## Day 2 (Tuesday)

### Task 1: Process Datasets (3 hours)

```bash
# Activate environment
source venv/bin/activate

# Process Dataset 1: Financial Scams
python data_pipeline/process_dataset.py \
    --input stream_a_datasets/financial_scams_detection_dataset.csv \
    --output stream_a_datasets/clean_dataset_1.csv \
    --profile stream_a_datasets/table1_stats_dataset1.json

# Process Dataset 2: BanglaBarta
python data_pipeline/process_dataset.py \
    --input stream_a_datasets/banglabarta_dataset.csv \
    --output stream_a_datasets/clean_dataset_2.csv \
    --profile stream_a_datasets/table1_stats_dataset2.json
```

**What this does:**
- De-identifies PII (phone numbers, NIDs)
- Extracts 30+ features per message
- Generates Table 1 statistics
- Creates clean, analysis-ready CSVs

### Task 2: Read TI-Bangladesh Report (2 hours)

**Focus on extracting these specific numbers:**
- Table 3: Fraud victimization rates (6.3% individuals, 17% agents)
- Financial loss ranges (BDT 300 - 376,000)
- Fraud methods (52.6% deceptive info, 42.1% phone/SMS)
- Complaint behavior (58.8% never file)
- Agent training gaps (90.3% never trained)
- MFS vs bank charges comparison

**Create a file:** `notes/ti_bangladesh_key_stats.txt` — paste all extracted numbers here.

### Task 3: Start Background Reading (1 hour)

Read ONE landmark paper today:
- **Miramirkhani et al., "Dial One for Scam" (NDSS 2017)**
- Focus: How they framed contributions, structured data collection, handled ethics

**Deliverable by end of Day 2:**
- [ ] Both datasets processed with Table 1 stats generated
- [ ] TI report key stats extracted
- [ ] First landmark paper read

---

## Day 3 (Wednesday)

### Task 1: Begin Data Collection — Telegram (2 hours)

```bash
# Run Telegram scraper
python stream_d_social_media/telegram_scraper.py \
    --all-known \
    --output ./telegram_data
```

**This will scrape:**
- @LGPaymentgateway (~103 posts)
- @ag4566 (~50 posts)

**While this runs, do Task 2 simultaneously.**

### Task 2: Prepare IRB Submission (3 hours)

**At East-West University, submit to:** Research Ethics Committee

**Your IRB package needs:**
1. **Research protocol** (use this as template):

```
TITLE: Measuring Mobile Financial Service (MFS) Scam Ecosystems in Bangladesh

PRINCIPAL INVESTIGATOR: [Your name], [Your department], East-West University

RESEARCH OBJECTIVES:
1. Characterize the types and prevalence of MFS scams targeting Bangladeshi users
2. Analyze scam distribution across channels (SMS, social media, email)
3. Map the infrastructure used by scam operators
4. Measure user susceptibility factors
5. Develop and evaluate detection approaches

METHODOLOGY:
- Collection of publicly available scam messages (no human subjects)
- User survey (anonymous, voluntary, 12 minutes)
- Social media analysis of public content only
- Infrastructure analysis of publicly reported phishing URLs

DATA SOURCES:
1. Public datasets (Mendeley, CC-BY license)
2. Crowdsourced scam messages via Google Forms
3. Public Telegram channels and Facebook pages
4. Public phishing intelligence feeds (PhishTank, OpenPhish)
5. Anonymous user survey

PARTICIPANTS (Survey):
- Target: 400 adults (18+) in Bangladesh
- Recruitment: University networks, community organizations
- Compensation: None (voluntary)

INFORMED CONSENT:
- Electronic consent via checkbox before survey
- Bangla + English bilingual consent statement
- Right to withdraw at any time

DATA PROTECTION:
- No collection of: real transaction data, account numbers, NIDs
- All data stored encrypted
- Personal identifiers removed before analysis
- Data retained for 3 years, then securely deleted
- Publication in anonymized, aggregated form only

RISKS:
- Minimal. No sensitive personal data collected.
- Survey responses are anonymous.
- No deception involved.

BENEFITS:
- Societal: Improved understanding of MFS fraud ecosystem
- Practical: Better detection and prevention tools
- Academic: First comprehensive measurement study
```

2. **Consent form** (generated survey form has this built-in)
3. **Survey instrument** (`survey_form/survey_form.html`)
4. **Data Management Plan** (describe storage, sharing, deletion)

### Task 3: Start App Review Collection (runs in background)

```bash
# This takes ~30-60 minutes. Run in a separate terminal.
python stream_e_app_reviews/app_review_scraper.py \
    --all \
    --count 5000 \
    --output ./app_reviews
```

**Deliverable by end of Day 3:**
- [ ] Telegram scraper run (data collected)
- [ ] IRB package prepared
- [ ] App review collection started

---

## Day 4 (Thursday)

### Task 1: Submit IRB (2 hours)

- Print/submit IRB package to East-West University Research Ethics Committee
- Expected timeline: 4-6 weeks for approval
- Ask for expedited review (minimal risk study)

### Task 2: Start Phishing URL Collection (1 hour)

```bash
python stream_c_phishing_urls/phishing_pipeline.py \
    --refresh-all \
    --enrich \
    --output ./phishing_data
```

### Task 3: Continue Reading Landmark Papers (2 hours)

Read these two papers today:
- **Kanich et al., "Spamalytics" (ACM CCS 2008)** — measurement methodology
- **Oest et al., "PhishTime" (USENIX Security 2020)** — longitudinal measurement

**For each paper, write a 1-page summary noting:**
- How they collected data
- How they handled ethics
- How they structured results
- What you can replicate/adapt

Save summaries in `notes/reading_log.md`

### Task 4: Set Up CT Monitoring (30 minutes)

```bash
python infrastructure_monitoring/ct_monitor.py \
    --brands all \
    --days 30 \
    --output ./ct_monitor
```

**Deliverable by end of Day 4:**
- [ ] IRB submitted
- [ ] Phishing collection started
- [ ] 3 landmark papers read
- [ ] CT monitoring running

---

## Day 5 (Friday)

### Task 1: Verify Data Collection Status (1 hour)

Check what has been collected so far:

```bash
# Check Telegram data
ls -lh telegram_data/raw/
ls -lh telegram_data/processed/

# Check app reviews
ls -lh app_reviews/

# Check phishing URLs
ls -lh phishing_data/enriched/
ls -lh phishing_data/reports/

# Check CT monitor
ls -lh ct_monitor/
```

### Task 2: Read Remaining Landmark Papers (3 hours)

- **Xu et al., "The Anatomy of a Cryptocurrency Pump-and-Dump Scheme" (IMC 2019)**
- **Thomas et al., "Data Breaches, Phishing, or Malware?" (ACM CCS 2017)**

### Task 3: Write Literature Review Draft (2 hours)

**Structure into 5 clusters:**

```markdown
## Related Work

### 2.1 Phishing and Smishing Measurement
[Paragraph on Dial One for Scam, PhishTime, Spamalytics]

### 2.2 MFS Fraud in the Global South
[Paragraph on mobile money fraud in Africa, few Bangladesh-specific works]

### 2.3 Scam Campaign Infrastructure Analysis
[Paragraph on domain clustering, ASN analysis]

### 2.4 NLP-based Fraud Detection
[Paragraph on BanglaBERT, prior smishing detection]

### 2.5 User Susceptibility and Awareness
[Paragraph on digital literacy, survey-based studies]

### Gap Statement
No prior work has comprehensively measured the MFS scam ecosystem in Bangladesh 
combining multi-channel data with user susceptibility analysis and infrastructure mapping.
```

**Deliverable by end of Day 5 (END OF WEEK 1):**
- [ ] IRB submitted to university
- [ ] Both datasets processed and profiled
- [ ] Telegram data collected
- [ ] App reviews collected (or collecting)
- [ ] Phishing URLs collecting
- [ ] CT monitoring running
- [ ] 5 landmark papers read
- [ ] Literature review drafted
- [ ] TI-Bangladesh key stats extracted

---

# PHASE 1: DATA COLLECTION ENGINE (Weeks 2-4)
## Goal: All data streams running, survey deployed, crowdsourcing active

---

## Week 2 Plan

### Monday: Deploy Survey

**Only after IRB approval** (if not approved yet, prepare everything and wait):

```bash
# Generate final survey
python survey_form/survey_toolkit.py --generate --output ./survey

# Import survey_form.html into Google Forms:
# 1. Open Google Forms (forms.google.com)
# 2. Create new blank form
# 3. Manually recreate questions using survey_form.html as reference
# 4. Add IRB approval number to header
# 5. Set response destination to Google Sheets
# 6. Get shareable link
```

**Survey deployment checklist:**
- [ ] All 33 questions entered in Google Forms
- [ ] Consent checkbox at top (required)
- [ ] Bangla translations reviewed by native speaker
- [ ] IRB approval number in header
- [ ] Response sheet linked
- [ ] Shareable link generated
- [ ] Test response submitted and verified

### Tuesday: Begin Survey Distribution

**Recruitment strategy (target: 500 responses for 400 valid):**

| Channel | How | Expected Responses |
|---------|-----|-------------------|
| University students | Department email, class announcements | 150 |
| Student associations | Partner with CSE club, IEEE SB | 100 |
| Social media | Facebook groups (university, local) | 100 |
| Union Digital Centers | Visit 2-3 centers in Dhaka | 50 |
| Personal network | WhatsApp groups, friends/family | 50 |
| NGOs | Contact digital literacy programs | 50 |

**Recruitment message template:**
```
Research Participation Invitation

We are conducting a study on Mobile Financial Services (MFS) fraud 
in Bangladesh. The survey takes 12 minutes and is completely anonymous.

Your participation will help improve fraud detection and prevention.

[Google Forms Link]

Approved by East-West University Research Ethics Committee
[IRB Number]
```

### Wednesday-Friday: Crowdsourced Message Collection

```bash
# Launch Google Form for scam message submission
# Create a NEW form with these fields:
```

**Scam Submission Form fields:**
1. Your scam message (text area, required)
2. Delivery channel (dropdown: SMS / WhatsApp / Facebook / Email / Phone call / Other)
3. Approximate date received (date picker)
4. Did you report it? (Yes / No / Not sure)
5. Were you financially harmed? (Yes / No)
6. Consent checkbox (required): "I consent to sharing this message for research purposes"

### Daily throughout Week 2: Monitor Collection

```bash
# Check app reviews
python stream_e_app_reviews/app_review_scraper.py --all --count 5000 --output ./app_reviews

# Re-run phishing pipeline (updates data)
python stream_c_phishing_urls/phishing_pipeline.py --refresh-all --enrich --output ./phishing_data

# Re-run CT monitor
python infrastructure_monitoring/ct_monitor.py --brands all --days 30 --output ./ct_monitor

# Scrape more Telegram channels (if you discover new ones)
python stream_d_social_media/telegram_scraper.py --channel CHANNEL_NAME --output ./telegram_data
```

### Week 2 Deliverables:
- [ ] Survey deployed and collecting responses
- [ ] Scam submission form live
- [ ] Active recruitment across 6 channels
- [ ] App reviews: 15,000-20,000 collected
- [ ] Phishing URLs: 50-200 BD-brand URLs
- [ ] CT monitor: suspicious domains flagged

---

## Week 3 Plan

### Monday-Wednesday: Recruit and Train Annotators

**Who to recruit:**
- 2 fellow students (NOT from your research group)
- Must be native Bangla speakers
- Must be comfortable reading Romanized Bangla

**Training session (2 hours):**

1. **Introduction (15 min)**
   - Explain the research
   - Show them the 7-category taxonomy
   - Explain inter-annotator agreement

2. **Codebook Review (30 min)**
   - Walk through each category with examples
   - Show Bangla + English examples
   - Discuss ambiguous cases

3. **Pilot Annotation (45 min)**
   - Both annotate same 20 messages
   - Compare results immediately
   - Discuss disagreements
   - Refine understanding

4. **Practice (30 min)**
   - Annotate 30 more messages independently
   - Calculate pilot Kappa
   - Target: Kappa > 0.60 acceptable for pilot

### Thursday-Friday: Begin Large-Scale Annotation

```bash
# Launch annotation interface
python annotation_interface/annotation_tool.py \
    --setup \
    --dataset stream_a_datasets/clean_dataset_1.csv \
    --output ./annotation

# Open annotation_interface.html in browser
# Give annotators the file or host it on a simple HTTP server
```

**Annotation workflow:**
1. Each annotator gets their own copy of `annotation_interface.html`
2. They annotate independently (do NOT discuss)
3. Target: 100 messages per day per annotator
4. Track progress daily
5. Check agreement every 200 messages

### Week 3 Deliverables:
- [ ] 2 annotators recruited and trained
- [ ] Pilot annotation complete (Kappa > 0.60)
- [ ] 400-600 messages annotated
- [ ] Survey responses: 200+ collected
- [ ] Scam submissions: 50+ collected

---

## Week 4 Plan

### Monday-Wednesday: Continue Annotation

- Target: 800-1000 messages fully annotated
- Check inter-annotator agreement every 200 messages
- If Kappa drops below 0.70, retrain on problematic categories

**To check agreement mid-way:**
```bash
# Export annotations from both annotators
# Then run:
python annotation_interface/annotation_tool.py \
    --agreement \
    --annotations annotator1_export.csv annotator2_export.csv \
    --report iaa_report_midway.json
```

### Thursday: Facebook Data Collection

```bash
# Install Chrome + ChromeDriver first
# Then run Facebook scraper with Selenium

python stream_d_social_media/facebook_scraper.py \
    --page PAGE_NAME \
    --selenium \
    --max-posts 50 \
    --output ./facebook_data
```

**Pages to target (discover via search):**
- Search Facebook for: "bKash offer", "Nagad bonus", "free taka"
- Document any public pages posting scam offers
- Screenshot posts for evidence

### Friday: Week 4 Review

**Check all data streams:**
```
Dataset 1 (Financial Scams):     [XXXX] messages
Dataset 2 (BanglaBarta):          2,772 messages (complete)
Telegram channels:                [XXXX] posts
App reviews:                      [XXXX] reviews
Phishing URLs:                    [XXXX] URLs
CT suspicious domains:            [XXXX] domains
Survey responses:                 [XXXX] responses
Scam submissions:                 [XXXX] messages
Annotated messages:               [XXXX] messages
```

### Week 4 Deliverables:
- [ ] 1000+ messages annotated (target: 70% of dataset)
- [ ] Inter-annotator agreement checked (Kappa > 0.70)
- [ ] Facebook data collected
- [ ] Survey: 300+ responses
- [ ] Scam submissions: 100+ messages
- [ ] All automated pipelines running

---

# PHASE 2: DATASET CONSTRUCTION (Weeks 5-6)
## Goal: Clean, annotated, versioned dataset ready for analysis

---

## Week 5 Plan

### Monday-Tuesday: Complete Annotation

- Finish annotating remaining messages
- Final inter-annotator agreement check

```bash
# Final IAA calculation
python annotation_interface/annotation_tool.py \
    --agreement \
    --annotations annotator1_final.csv annotator2_final.csv \
    --report iaa_report_final.json
```

**Target: Cohen's Kappa >= 0.80**

If Kappa < 0.80:
1. Identify categories with lowest agreement
2. Both annotators review those categories with you
3. Re-annotate disputed messages
4. Recalculate

### Wednesday: Merge and Clean Dataset

```bash
# Merge both annotators' labels
# Resolve disagreements (majority vote or your adjudication)

# Create final annotated dataset with columns:
# message_id, text, annotator1_label, annotator2_label, final_label, 
# agreement_flag, notes
```

**Use Python script:**
```python
import pandas as pd

# Load both annotation files
a1 = pd.read_csv('annotator1_final.csv')
a2 = pd.read_csv('annotator2_final.csv')

# Merge on message_id
merged = pd.merge(a1, a2, on='message_id', suffixes=('_a1', '_a2'))

# Resolve disagreements (majority vote, or you as tie-breaker)
merged['final_label'] = merged.apply(
    lambda row: row['category_a1'] if row['category_a1'] == row['category_a2'] else 'ADJUDICATE',
    axis=1
)

# Save disagreements for manual review
disagreements = merged[merged['final_label'] == 'ADJUDICATE']
print(f"Disagreements to adjudicate: {len(disagreements)}")

# After manual adjudication, save final dataset
merged.to_csv('final_annotated_dataset.csv', index=False)
```

### Thursday: Merge All Data Sources

```python
import pandas as pd

# Load all data sources
ds1 = pd.read_csv('stream_a_datasets/clean_dataset_1.csv')  # Financial Scams
ds2 = pd.read_csv('stream_a_datasets/clean_dataset_2.csv')  # BanglaBarta
telegram = pd.read_csv('telegram_data/processed/LGPaymentgateway_20260524.csv')
app_reviews = pd.read_csv('app_reviews/mfs_app_reviews.csv')
survey = pd.read_csv('survey/responses.csv')  # from Google Forms

# Merge datasets 1 and 2 (they have different columns, standardize)
print(f"Dataset 1: {len(ds1)} rows")
print(f"Dataset 2: {len(ds2)} rows")
print(f"Telegram: {len(telegram)} rows")
print(f"App reviews: {len(app_reviews)} rows")
print(f"Survey: {len(survey)} rows")

# Create combined corpus
# ...standardize columns...
```

### Friday: Dataset Documentation + Zenodo Deposit

**Create README for dataset:**
```markdown
# Bangladesh MFS Scam Ecosystem Dataset v1.0

## Description
Multi-source corpus of MFS scam messages collected from 
SMS, Telegram, app reviews, and crowdsourced submissions.

## Sources
1. Financial Scams Detection Dataset (Mendeley, CC-BY)
2. BanglaBarta (Mendeley, CC BY-NC-SA)
3. Telegram public channels
4. Google Play app reviews
5. Crowdsourced submissions (with consent)

## Schema
[Describe each column]

## Labels
1. Account Compromise
2. Fake Promotional Offer
3. Lottery/Prize Scam
4. Loan/Job Scam
5. Impersonation
6. Phishing Link
7. Legitimate (Ham)

## Statistics
[Total messages, label distribution, language distribution]

## Inter-Annotator Agreement
Cohen's Kappa: [value]

## Ethics
[IRB approval number, consent procedures, data handling]

## Citation
[Cite this dataset]
```

**Deposit on Zenodo:**
1. Go to https://zenodo.org
2. Create account (use institutional email)
3. "New Upload" → upload final dataset + README
4. Add metadata:
   - Title: "Bangladesh MFS Scam Ecosystem Dataset"
   - Authors: [Your name]
   - Keywords: smishing, mobile financial services, fraud, Bangladesh
   - License: CC-BY-4.0
5. Publish → get DOI

### Week 5 Deliverables:
- [ ] Annotation complete with Kappa >= 0.80
- [ ] Disagreements resolved
- [ ] Dataset merged and cleaned
- [ ] README written
- [ ] Dataset deposited on Zenodo with DOI

---

## Week 6 Plan

### Monday-Wednesday: Dataset Freeze + Final Processing

**Dataset is FROZEN — no more additions.**

```bash
# Run final processing pipeline
python data_pipeline/process_dataset.py \
    --input final_annotated_dataset.csv \
    --output final_processed_dataset.csv \
    --profile final_dataset_profile.json

# Generate all Table 1 statistics
python -c "
import json
with open('final_dataset_profile.json') as f:
    profile = json.load(f)
print('=== TABLE 1: DATASET PROFILE ===')
print(f'Total samples: {profile[\"total_samples\"]}')
print(f'Label distribution: {profile[\"label_distribution\"]}')
print(f'Language composition: {profile[\"language_stats\"]}')
print(f'Message length: {profile[\"text_stats\"]}')
"
```

### Thursday-Friday: Prepare Survey Data for Analysis

```bash
# Process survey responses
python survey_form/survey_toolkit.py \
    --process survey/responses.csv \
    --report survey/survey_report.json
```

**Survey analysis includes:**
- Digital literacy score computation
- Susceptibility score computation  
- Demographic breakdown
- Scam exposure statistics
- Regression model preparation

### Week 6 Deliverables:
- [ ] Dataset FROZEN (v1.0 on Zenodo)
- [ ] Final Table 1 statistics generated
- [ ] Survey data processed and analyzed
- [ ] All data ready for measurement analysis

---

# PHASE 3: MEASUREMENT + ANALYSIS (Weeks 7-12)
## Goal: Answer all Research Questions with statistical rigor

---

## Research Questions to Answer

| RQ | Question | Analysis Method | Output |
|----|----------|----------------|--------|
| RQ1 | What are dominant scam types and proportions? | Descriptive stats, prevalence rates | Tables, pie charts |
| RQ2 | How do scams differ across channels? | Linguistic analysis, cross-channel comparison | Heatmaps, bar charts |
| RQ3 | What infrastructure do operators reuse? | Domain clustering, ASN analysis | Network graphs, CDFs |
| RQ4 | How accurately can classifiers detect scams? | ML experiments, ablation studies | Results table |
| RQ5 | What user factors correlate with susceptibility? | Regression analysis | Regression table |

---

## Week 7: RQ1 — Scam Ecosystem Characterization

### Monday: Category Prevalence

```python
import pandas as pd
import numpy as np
from scipy import stats

# Load dataset
df = pd.read_csv('final_processed_dataset.csv')

# Category prevalence
prevalence = df['final_label'].value_counts(normalize=True) * 100
print("=== RQ1a: Category Prevalence ===")
print(prevalence)

# 95% confidence intervals
from statsmodels.stats.proportion import proportion_confint
n = len(df)
for cat, count in df['final_label'].value_counts().items():
    ci_low, ci_high = proportion_confint(count, n, alpha=0.05, method='wilson')
    print(f"{cat}: {count/n*100:.1f}% (95% CI: {ci_low*100:.1f}%-{ci_high*100:.1f}%)")
```

### Tuesday: Temporal Patterns

```python
# Convert timestamps
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['month'] = df['timestamp'].dt.to_period('M')
df['hour'] = df['timestamp'].dt.hour

# Monthly trends
monthly = df.groupby(['month', 'final_label']).size().unstack(fill_value=0)
monthly.plot(kind='line', figsize=(12, 6))
plt.title('Scam Type Trends Over Time')
plt.savefig('figures/temporal_trends.png')

# Hour-of-day distribution
hourly = df.groupby(['hour', 'final_label']).size().unstack(fill_value=0)
```

### Wednesday: Channel Distribution

```python
# Channel distribution
channel_dist = pd.crosstab(df['channel'], df['final_label'], normalize='index') * 100
print("=== RQ1c: Channel Distribution ===")
print(channel_dist)

# Chi-squared test
chi2, p, dof, expected = stats.chi2_contingency(pd.crosstab(df['channel'], df['final_label']))
print(f"Chi-squared: {chi2:.2f}, p-value: {p:.4f}")
```

### Thursday: Geographic + Demographic (from survey)

```python
# Load survey data
survey = pd.read_csv('survey/responses.csv')

# Urban vs rural scam exposure
geo_cross = pd.crosstab(survey['A4'], survey['C1'], normalize='index') * 100
print("=== Geographic Distribution ===")
print(geo_cross)

# Age group analysis
age_cross = pd.crosstab(survey['A1'], survey['C1'], normalize='index') * 100
```

### Friday: Document RQ1 Results

Create:
- `results/rq1_prevalence_table.md` — Table with all prevalence stats + CIs
- `figures/rq1_category_distribution.png` — Pie/bar chart
- `figures/rq1_temporal_trends.png` — Time series
- `figures/rq1_channel_distribution.png` — Cross-channel comparison

---

## Week 8: RQ2 — Linguistic and Structural Analysis

### Monday: Urgency Framing Analysis

```python
URGENCY_WORDS = ['urgent', 'immediately', 'now', 'today', 'hurry', 
                 'expires', 'deadline', 'limited', 'act now', 
                 'জরুরি', 'এখনি', 'আজই', 'দ্রুত', 'শেষ', 'সীমিত']

def count_urgency_words(text):
    text_lower = text.lower()
    return sum(1 for w in URGENCY_WORDS if w in text_lower)

df['urgency_count'] = df['text'].apply(count_urgency_words)
df['has_urgency'] = df['urgency_count'] > 0

# Urgency by scam type
urgency_by_type = df.groupby('final_label')['has_urgency'].mean() * 100
print("=== RQ2a: Urgency Framing by Type ===")
print(urgency_by_type)

# Mann-Whitney U test: scam vs ham
scam = df[df['final_label'] != 'Legitimate']['urgency_count']
ham = df[df['final_label'] == 'Legitimate']['urgency_count']
u_stat, p = stats.mannwhitneyu(scam, ham, alternative='two-sided')
print(f"Mann-Whitney U: {u_stat:.2f}, p: {p:.4f}")
```

### Tuesday: Language Mixing Analysis

```python
# Bangla ratio per category
def bangla_ratio(text):
    bangla_chars = sum(1 for c in text if '\u0980' <= c <= '\u09FF')
    total = sum(1 for c in text if c.isalpha())
    return bangla_chars / total if total > 0 else 0

df['bangla_ratio'] = df['text'].apply(bangla_ratio)
df['is_code_mixed'] = (df['bangla_ratio'] > 0) & (df['bangla_ratio'] < 1)

# Code-mixing by category
code_mix = df.groupby('final_label')['is_code_mixed'].mean() * 100
print("=== RQ2b: Code-Mixing by Type ===")
print(code_mix)

# Compare scam vs legitimate
scam_cm = df[df['final_label'] != 'Legitimate']['is_code_mixed'].mean()
ham_cm = df[df['final_label'] == 'Legitimate']['is_code_mixed'].mean()
print(f"Scam code-mixing: {scam_cm*100:.1f}%")
print(f"Legitimate code-mixing: {ham_cm*100:.1f}%")
```

### Wednesday: Call-to-Action Analysis

```python
CTA_PATTERNS = {
    'send_otp': r'\bOTP\b.*\b(send|give|share)\b|\b(send|give|share)\b.*\bOTP\b',
    'click_url': r'\bclick\b.*\b(link|here|url)\b|\b(link|url)\b.*\bclick\b',
    'call_number': r'\bcall\b.*\b(number|now)\b|\bphone\b.*\bcall\b',
    'send_money': r'\bsend\b.*\b(money|taka|tk)\b|\b(money|taka|tk)\b.*\bsend\b',
}

for cta_name, pattern in CTA_PATTERNS.items():
    df[f'cta_{cta_name}'] = df['text'].str.contains(pattern, case=False, regex=True)

# CTA distribution by scam type
cta_cols = [c for c in df.columns if c.startswith('cta_')]
cta_by_type = df.groupby('final_label')[cta_cols].mean() * 100
print("=== RQ2c: Call-to-Action Distribution ===")
print(cta_by_type)
```

### Thursday: Named Entity Analysis

```python
# Brand mention frequency by category
brand_mentions = df.groupby('final_label')[['mentions_bkash', 'mentions_nagad', 'mentions_rocket']].mean() * 100
print("=== RQ2d: Brand Mention Frequency ===")
print(brand_mentions)
```

### Friday: Document RQ2 Results

Create:
- `results/rq2_linguistic_analysis.md`
- `figures/rq2_urgency_heatmap.png`
- `figures/rq2_code_mixing.png`
- `figures/rq2_cta_distribution.png`

---

## Week 9: RQ3 — Infrastructure Analysis

### Monday-Wednesday: Phishing URL Analysis

```python
# Load enriched phishing data
phishing = pd.read_csv('phishing_data/enriched/phishing_urls.csv')

# Domain clustering by ASN
asn_clusters = phishing.groupby('hosting_asn')['domain'].nunique().sort_values(ascending=False)
print("=== RQ3a: Domain Clustering by ASN ===")
print(asn_clusters.head(20))

# TLD analysis
tld_dist = phishing['tld'].value_counts()
print("=== RQ3b: TLD Distribution ===")
print(tld_dist.head(10))

# URL shortener usage
shortener_pct = phishing['uses_url_shortener'].mean() * 100
print(f"URL shortener usage: {shortener_pct:.1f}%")

# Hosting geography
hosting_geo = phishing['hosting_country'].value_counts()
print("=== RQ3c: Hosting Geography ===")
print(hosting_geo.head(10))

# HTTPS adoption
https_pct = phishing['has_https'].mean() * 100
print(f"HTTPS adoption: {https_pct:.1f}%")
```

### Thursday: Certificate Transparency Analysis

```python
# Load CT monitor results
ct_results = pd.read_csv('ct_monitor/alerts/suspicious_20260524.csv')

# Risk score distribution
print(f"Total suspicious domains: {len(ct_results)}")
print(f"High risk (score >= 5): {len(ct_results[ct_results['risk_score'] >= 5])}")

# By brand
by_brand = ct_results['brand'].value_counts()
print("=== Suspicious Domains by Brand ===")
print(by_brand)
```

### Friday: Document RQ3 Results

Create:
- `results/rq3_infrastructure_analysis.md`
- `figures/rq3_asn_clusters.png`
- `figures/rq3_tld_distribution.png`
- `figures/rq3_hosting_map.png`

---

## Week 10: RQ4 — Detection System (Baselines)

### Monday: Set Up ML Environment

```bash
pip install scikit-learn transformers datasets torch tensorflow
pip install bangla-bert  # if available
```

### Tuesday-Wednesday: Baseline Classifiers

```python
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, f1_score, roc_auc_score
import numpy as np

# Prepare data
X = df['text']
y = df['final_label']

# 70/15/15 split
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42, stratify=y_temp)

# TF-IDF vectorizer
tfidf = TfidfVectorizer(max_features=10000, ngram_range=(1, 2))
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# Baselines
models = {
    'Naive Bayes': MultinomialNB(),
    'SVM': SVC(kernel='linear', probability=True),
    'Logistic Regression': LogisticRegression(max_iter=1000),
}

results = {}
for name, model in models.items():
    model.fit(X_train_tfidf, y_train)
    y_pred = model.predict(X_test_tfidf)
    f1 = f1_score(y_test, y_pred, average='macro')
    results[name] = {'macro_f1': f1}
    print(f"{name}: Macro F1 = {f1:.4f}")
```

### Thursday-Friday: BanglaBERT Fine-tuning

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
import torch

# Load BanglaBERT
tokenizer = AutoTokenizer.from_pretrained("sagorsarker/bangla-bert-base")
model = AutoModelForSequenceClassification.from_pretrained(
    "sagorsarker/bangla-bert-base", 
    num_labels=7
)

# Prepare datasets
train_encodings = tokenizer(X_train.tolist(), truncation=True, padding=True, max_length=128)
val_encodings = tokenizer(X_val.tolist(), truncation=True, padding=True, max_length=128)

# Convert to PyTorch datasets
class ScamDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item
    def __len__(self):
        return len(self.labels)

train_dataset = ScamDataset(train_encodings, y_train.map(label2id))
val_dataset = ScamDataset(val_encodings, y_val.map(label2id))

# Training arguments
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    warmup_steps=100,
    weight_decay=0.01,
    logging_dir='./logs',
    evaluation_strategy='epoch',
)

# Train
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
)
trainer.train()

# Evaluate
predictions = trainer.predict(val_dataset)
# Calculate metrics
```

### Week 10 Deliverables:
- [ ] Baseline classifiers trained and evaluated
- [ ] BanglaBERT fine-tuned
- [ ] Results comparison table

---

## Week 11: RQ4 — Ablation + Error Analysis

### Monday: Ablation Study

```python
# Ablation: Remove Bangla text
X_train_en = X_train.apply(remove_bangla)
X_test_en = X_test.apply(remove_bangla)
# Retrain and compare

# Ablation: Remove URL features
X_train_no_url = X_train.apply(remove_urls)
X_test_no_url = X_test.apply(remove_urls)
# Retrain and compare

# Ablation: Remove named entity features
X_train_no_ne = X_train.apply(remove_brand_names)
X_test_no_ne = X_test.apply(remove_brand_names)
# Retrain and compare
```

### Tuesday: Error Analysis

```python
# Identify false positives and false negatives
y_pred = model.predict(X_test_tfidf)
fp = X_test[(y_test == 'Legitimate') & (y_pred != 'Legitimate')]
fn = X_test[(y_test != 'Legitimate') & (y_pred == 'Legitimate')]

# Analyze 50 samples of each
print("=== FALSE POSITIVES (Legitimate flagged as scam) ===")
for msg in fp.head(50):
    print(f"- {msg[:100]}...")

print("\n=== FALSE NEGATIVES (Scams missed) ===")
for msg in fn.head(50):
    print(f"- {msg[:100]}...")
```

### Wednesday: Cross-Validation

```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
cv_scores = cross_val_score(model, X_train_tfidf, y_train, cv=skf, scoring='f1_macro')
print(f"5-fold CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
```

### Thursday-Friday: Document RQ4 Results

Create:
- `results/rq4_detection_system.md`
- `figures/rq4_results_table.png` — comparison of all models
- `figures/rq4_ablation_study.png` — feature contribution
- `figures/rq4_confusion_matrix.png`

---

## Week 12: RQ5 — User Susceptibility Analysis

### Monday: Regression Model

```python
import statsmodels.api as sm
from statsmodels.stats.outliers_influence import variance_inflation_factor

# Load survey with computed scores
survey = pd.read_csv('survey/survey_with_scores.csv')

# Dependent variable: susceptibility_score (higher = more susceptible)
# Independent variables: demographics + digital literacy

# Encode categorical variables
survey['gender_male'] = (survey['A2'] == 'Male').astype(int)
survey['education_college'] = survey['A3'].isin(["Bachelor's", "Master's+"])..astype(int)
survey['urban'] = (survey['A4'] == 'Urban (city)').astype(int)
survey['age_25_34'] = (survey['A1'] == '25-34').astype(int)

# OLS regression
X = survey[['digital_literacy_score', 'gender_male', 'education_college', 
             'urban', 'age_25_34', 'scam_exposure_count']]
X = sm.add_constant(X)
y = survey['susceptibility_score']

model = sm.OLS(y, X).fit()
print(model.summary())
```

### Tuesday-Friday: Document RQ5 + Synthesize All Results

Create:
- `results/rq5_susceptibility_analysis.md`
- `figures/rq5_regression_table.png`
- Synthesize all RQ findings into coherent narrative

### Week 12 Deliverables:
- [ ] RQ1-RQ5 all answered with statistical rigor
- [ ] All figures generated
- [ ] All results tables created
- [ ] Detection system evaluated
- [ ] Model weights saved for artifact submission

---

# PHASE 4: PAPER WRITING (Weeks 13-18)
## Goal: Complete paper draft ready for submission

---

## Week 13: Write Data Collection + Results Sections

**These are the hardest and most important sections — write them first.**

### Monday-Tuesday: Data Collection Section (2 pages)

**Structure:**
```
3. Data Collection
3.1 Overview — Describe all 5 data sources
3.2 SMS Message Corpus — Mendeley datasets + crowdsourced
3.3 Social Media Corpus — Telegram + Facebook
3.4 User-Generated Reviews — App store reviews
3.5 Phishing URL Feed — PhishTank + OpenPhish
3.6 User Survey — Design, deployment, recruitment
3.7 Ethics Considerations — IRB, consent, data handling
3.8 Dataset Profile — Table 1 with all statistics
```

### Wednesday-Friday: Measurement Results Section (3-4 pages)

**Structure:**
```
4. Measurement Results
4.1 Scam Ecosystem Characterization (RQ1)
    — Category prevalence with CIs
    — Temporal patterns
    — Channel distribution
4.2 Linguistic and Structural Analysis (RQ2)
    — Urgency framing
    — Code-mixing patterns
    — Call-to-action analysis
    — Brand impersonation
4.3 Infrastructure Analysis (RQ3)
    — Domain clustering
    — TLD abuse
    — Hosting geography
    — URL shortener usage
```

---

## Week 14: Write Remaining Sections

### Monday: Detection System Section (2-3 pages)

```
5. Detection System (RQ4)
5.1 Baseline Classifiers
5.2 BanglaBERT Fine-tuning
5.3 Ablation Study
5.4 Error Analysis
5.5 Results Comparison Table
```

### Tuesday: User Study Section (1-2 pages)

```
6. User Susceptibility Analysis (RQ5)
6.1 Survey Design
6.2 Participant Demographics (Table)
6.3 Digital Literacy Scores
6.4 Susceptibility Regression Model
6.5 Key Findings
```

### Wednesday: Introduction + Background

**Introduction (1.5-2 pages):**
```
1. Introduction
- Hook: $1.9B lost, 6.3% victimization rate
- Problem: No prior measurement study
- Research Questions (list RQ1-RQ5)
- Contributions (bulleted list):
  1. First multi-source dataset of BD MFS scams
  2. Comprehensive taxonomy with IAA
  3. Cross-channel measurement analysis
  4. Detection system with BanglaBERT
  5. User susceptibility model
- Paper roadmap
```

**Background (0.5-1 page):**
```
2. Background
2.1 Bangladesh MFS Ecosystem — bKash, Nagad, Rocket, market share
2.2 Regulatory Context — Bangladesh Bank, CIRT
```

### Thursday: Related Work + Discussion

**Related Work (1 page):** Use your drafted literature review.

**Discussion (1 page):**
- Synthesize findings across all sections
- Implications for policy, platforms, users
- Responsible disclosure to CIRT

### Friday: Ethics + Limitations + Conclusion

**Ethics Considerations (0.5 page):**
- IRB approval status
- Data handling procedures
- Responsible disclosure actions
- Risks to participants and mitigations

**Limitations (0.5 page):**
- Sampling bias (urban/university overrepresented)
- Self-reported survey data
- No access to telecom operator data
- No longitudinal tracking
- Language limitations

**Conclusion (0.25 page):**
- Restate 3 most important findings
- One sentence on future work

---

## Week 15: Polish and Internal Review

### Monday-Tuesday: Abstract + Figures

**Abstract (250 words):**
```
- 1 sentence: Problem (MFS fraud in Bangladesh)
- 1 sentence: Why hard/novel (no prior measurement)
- 2 sentences: Method (multi-source dataset, taxonomy, measurement)
- 2 sentences: Key findings (prevalence, patterns, detection)
- 1 sentence: Contribution
```

**Final check on all figures:**
- [ ] All figures legible in grayscale
- [ ] All figures have captions
- [ ] Axis labels, units, error bars present
- [ ] Self-contained captions

### Wednesday-Thursday: Internal Review

**Send draft to 2 colleagues:**
1. One for technical correctness (CSE faculty/student)
2. One for clarity (someone unfamiliar with Bangladesh)

**Ask them specifically:**
- Are the statistics convincing?
- Is the methodology clear and reproducible?
- Are the claims supported by evidence?
- Is the contribution clearly stated?
- Are there any ethical concerns?

### Friday: Incorporate Feedback

Create revision log:
```
Reviewer 1 Feedback:
- [FIXED] Page 3: Clarified sample size calculation
- [FIXED] Page 5: Added confidence intervals to Table 2
- [PENDING] Page 8: Need more explanation of BanglaBERT

Reviewer 2 Feedback:
- [FIXED] Page 2: Explained bKash for international readers
- [FIXED] Page 6: Fixed typo in RQ3
```

---

## Week 16: Responsible Disclosure + Artifact Prep

### Monday: Send Responsible Disclosure

**Email to BGD e-GOV CIRT:**
```
To: info@cirt.gov.bd
Subject: Responsible Disclosure — MFS Fraud Infrastructure Research

Dear CIRT Team,

We are researchers from East-West University conducting a measurement 
study of mobile financial services (MFS) fraud ecosystems in Bangladesh.

We have identified active phishing domains and scam infrastructure 
targeting bKash and Nagad users. We are providing this information 
under responsible disclosure, 30 days before publication.

Attached: List of identified phishing domains and suspicious 
infrastructure.

We request acknowledgment of this disclosure for our research paper.

Best regards,
[Your name]
East-West University Bangladesh
```

### Tuesday-Thursday: Artifact Package

```
artifact_package/
|-- README.md                    # Instructions for reproduction
|-- Dockerfile                   # Container for reproducibility
|-- requirements.txt             # All Python dependencies
|-- datasets/
|   |-- bangladesh_mfs_scam_dataset_v1.0.csv
|   |-- README.md               # Dataset documentation
|-- code/
|   |-- data_collection/         # All scrapers
|   |-- data_processing/         # Cleaning + feature extraction
|   |-- analysis/                # All analysis scripts
|   |-- detection/               # ML model training + evaluation
|-- models/
|   |-- banglabert_finetuned/    # Model weights
|   |-- baseline_models/         # Trained baseline models
|-- results/
|   |-- figures/                 # All paper figures
|   |-- tables/                  # All paper tables
```

**Create requirements.txt:**
```
pandas==2.0.0
numpy==1.24.0
scikit-learn==1.3.0
transformers==4.35.0
torch==2.1.0
requests==2.31.0
beautifulsoup4==4.12.0
scipy==1.11.0
statsmodels==0.14.0
matplotlib==3.8.0
seaborn==0.13.0
```

### Friday: Final Polish

- [ ] Spell check entire paper (Grammarly)
- [ ] Verify all citations are correct format (IEEE for NDSS)
- [ ] Check page limit compliance
- [ ] Verify all URLs are accessible
- [ ] Archive web URLs using archive.org
- [ ] Check figure grayscale legibility
- [ ] Remove all self-identifying info (double-blind)

---

# PHASE 5: SUBMISSION (Weeks 17-20)
## Goal: Submit, survive review, revise, accept

---

## Week 17: Submit

### Monday: Final Checks

- [ ] Page limit: 13 pages (NDSS) or 12 pages (USENIX) + references
- [ ] Double-blind: No author names, affiliations, acknowledgments
- [ ] Ethics section present
- [ ] Artifact DOI included in paper
- [ ] References in correct format
- [ ] PDF compiles without errors

### Tuesday: Submit to NDSS

1. Create account on HotCRP (NDSS submission system)
2. Upload PDF
3. Fill submission form:
   - Title, abstract
   - Author info (will be hidden during review)
   - Ethics considerations checkbox
   - Artifact submission checkbox
   - Enter Zenodo DOI
4. Submit!

**NDSS Deadlines (typical):**
- Cycle 1: ~May (for February conference)
- Cycle 2: ~September (for February conference)
- Check: https://www.ndss-symposium.org/ndss2026/

---

## Week 18: Await Reviews (1-2 months)

During this time:
- Continue refining analysis
- Respond to any CIRT disclosure feedback
- Start planning next paper (there will be one!)

---

## Week 19-20: Rebuttal + Revision

### When Reviews Arrive:

**Step 1: Read all reviews twice before responding.**
**Step 2: Wait 24 hours before writing anything.**

### Rebuttal Structure:

```
We thank the reviewers for their constructive feedback.

Response to Reviewer A:
- Major concern 1: [Acknowledge] We have added ... [Action]
- Major concern 2: [Acknowledge] We have clarified ... [Action]
- Minor concern 1: [Acknowledge] Fixed in Section X

Response to Reviewer B:
...

Changes made:
1. Added Table 5 showing ...
2. Clarified methodology in Section 3.2
3. Added discussion of limitations
```

### Common Revision Requests:

| Request | How to Address |
|---------|---------------|
| "Small sample size" | Bootstrap CIs, acknowledge limitation, discuss generalizability |
| "Need more baselines" | Add 2-3 more classifiers, cite why they're relevant |
| "Ethics concerns"" | Add more detail on consent, de-identification, IRB |
| "Unclear contribution" | Strengthen gap statement, clarify novelty |
| "Missing related work" | Add 2-3 more papers, explain distinction |
| "Statistics weak"" | Add effect sizes, more rigorous tests |

### After Acceptance:

1. **Camera-ready submission:** Fix all reviewer concerns
2. **Copyright form:** Sign and submit
3. **Artifact evaluation:** Submit to AE committee
4. **Presentation prep:** Start thinking about your talk

---

# APPENDIX: WEEKLY CHECKLIST

Print this and check off each week:

## Week 1
- [ ] Virtual environment created
- [ ] Both Mendeley datasets downloaded
- [ ] TI-Bangladesh report downloaded
- [ ] Datasets processed through pipeline
- [ ] Table 1 stats generated
- [ ] Telegram scraper run successfully
- [ ] App review scraper started
- [ ] Phishing pipeline started
- [ ] CT monitor started
- [ ] IRB package prepared
- [ ] IRB submitted to university
- [ ] 5 landmark papers read
- [ ] Literature review drafted

## Week 2
- [ ] Survey deployed (after IRB approval)
- [ ] Scam submission form live
- [ ] Recruitment active across 6 channels
- [ ] 200+ survey responses
- [ ] 50+ scam submissions
- [ ] App reviews: 15,000+
- [ ] Phishing URLs: 50+

## Week 3
- [ ] 2 annotators recruited
- [ ] Training session completed
- [ ] Pilot annotation: Kappa > 0.60
- [ ] 400-600 messages annotated
- [ ] Facebook scraper tested

## Week 4
- [ ] 1000+ messages annotated
- [ ] Inter-annotator agreement: Kappa > 0.70
- [ ] Facebook data collected
- [ ] Survey: 300+ responses
- [ ] Scam submissions: 100+

## Week 5
- [ ] Annotation complete: Kappa >= 0.80
- [ ] Disagreements resolved
- [ ] Dataset merged
- [ ] README written
- [ ] Zenodo deposit with DOI

## Week 6
- [ ] Dataset FROZEN
- [ ] Final Table 1 stats
- [ ] Survey data processed

## Week 7
- [ ] RQ1 answered (prevalence, temporal, channel)
- [ ] All RQ1 figures and tables

## Week 8
- [ ] RQ2 answered (linguistic, code-mixing, CTA)
- [ ] All RQ2 figures and tables

## Week 9
- [ ] RQ3 answered (infrastructure, clustering)
- [ ] All RQ3 figures and tables

## Week 10
- [ ] Baseline classifiers trained
- [ ] BanglaBERT fine-tuned

## Week 11
- [ ] Ablation study complete
- [ ] Error analysis done
- [ ] Cross-validation results

## Week 12
- [ ] RQ5 answered (susceptibility regression)
- [ ] All RQ5 figures and tables
- [ ] All results synthesized

## Week 13
- [ ] Data Collection section written
- [ ] Measurement Results section written

## Week 14
- [ ] Detection System section written
- [ ] User Study section written
- [ ] Introduction written
- [ ] Background written
- [ ] Related Work written
- [ ] Discussion written
- [ ] Ethics + Limitations + Conclusion written

## Week 15
- [ ] Abstract written
- [ ] Figures finalized
- [ ] Internal review completed
- [ ] Feedback incorporated

## Week 16
- [ ] Responsible disclosure sent to CIRT
- [ ] Artifact package prepared
- [ ] Final polish complete

## Week 17
- [ ] Paper submitted to NDSS!

## Week 18-20
- [ ] Rebuttal written
- [ ] Revision submitted
- [ ] Camera-ready submitted
- [ ] Artifact evaluation submitted

---

# CONTINGENCY PLANS

## If IRB Takes Longer Than 4 Weeks
- Continue with non-human-subjects data only
- Focus on: phishing URLs, Telegram, app reviews, infrastructure
- Write survey section as "planned work"
- Submit paper without survey, add in revision

## If Dataset Is Smaller Than Expected
- Target: 1,500+ messages minimum for credible paper
- If < 1,000: Extend crowdsourcing campaign, discover more Telegram channels
- If < 500: Pivot to qualitative analysis + infrastructure focus

## If BanglaBERT Performance Is Poor
- Try mBERT (multilingual BERT) instead
- Reduce to binary classification (scam vs ham)
- Focus paper on measurement (RQ1-RQ3), reduce detection to shorter section

## If Paper Rejected
- EXPECT THIS. 80%+ of first submissions are rejected.
- Read reviews carefully
- Address every major concern
- Resubmit to next venue (USENIX Security has 3 deadlines/year)
- Consider splitting into two papers (measurement + detection)

## If Reviewers Question Validity of Crowdsourced Data
- Emphasize inter-annotator agreement (Kappa > 0.80)
- Compare against Mendeley dataset statistics
- Show cross-validation with expert annotator
- Add discussion of limitations

---

# RESOURCE CHECKLIST

## Accounts You Need
- [ ] Mendeley account (free) — for datasets
- [ ] Zenodo account (free) — for artifact DOI
- [ ] GitHub account (free) — for code repository
- [ ] Google account (free) — for Google Forms
- [ ] HotCRP account (free) — for NDSS submission
- [ ] Overleaf account (free) — for LaTeX writing

## Software You Need
- [ ] Python 3.8+ with virtual environment
- [ ] Chrome browser (for Selenium scrapers)
- [ ] LaTeX (Overleaf recommended)
- [ ] Grammar checker (Grammarly free tier)
- [ ] Reference manager (Zotero or Mendeley)

## Hardware You Need
- [ ] Personal computer (8GB RAM minimum, 16GB recommended)
- [ ] Reliable internet connection
- [ ] Backup drive/cloud storage for data

## Access You Need
- [ ] East-West University Research Ethics Committee
- [ ] University library (for paper access)
- [ ] Google Scholar (free)
- [ ] Telegram account (free — for channel discovery)
- [ ] Facebook account (free — for page discovery)

---

*Roadmap Version: 1.0*
*Generated: May 2026*
*Total Duration: 20 weeks (5 months)*
*Target Submission: NDSS 2027 (submit September 2026)*
