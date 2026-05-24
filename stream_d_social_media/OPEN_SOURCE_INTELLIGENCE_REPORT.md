# Open Source Intelligence Report: Bangladesh MFS Fraud Ecosystem
## Newly Discovered Data Sources, Datasets, and Real Intelligence

---

## EXECUTIVE SUMMARY

This report documents **4 major new data sources** discovered through open source intelligence gathering, including a **second public dataset** (2,772 Bangla SMS messages), a **government watchdog report** with detailed survey statistics, a **GitHub project** with crowd-sourced scam data, and the **largest institutional MFS fraud case** in Bangladesh's history (Tk 1,711 crore / ~$1.4B USD).

---

## 1. NEW PUBLIC DATASET: BanglaBarta (Mendeley)

### Overview
| Attribute | Detail |
|-----------|--------|
| **Name** | BangalaBarta: A Spam/Smishing SMS Dataset Bangla |
| **Source** | Mendeley Data |
| **DOI** | 10.17632/jfkfbw3gzh.2 |
| **Size** | 2,772 SMS messages |
| **Language** | Bangla (Bengali) |
| **Classes** | 3 (Smishing, Promotional, Normal) |
| **License** | CC BY-NC-SA 4.0 |
| **Published** | February 2025 (Version 2) |
| **Authors** | Md Farhan Shahriyar, Gazi Tanbhir |

### Dataset Composition
- **Smishing:** SMS messages designed to deceive users into revealing sensitive information
- **Promotional:** Marketing messages from various businesses
- **Normal SMS:** Everyday communication between users

### Telecom Coverage
- Grameenphone
- Banglalink
- Robi
- Other major Bangladeshi telecom operators

### Research Value
This dataset is **complementary** to the Financial Scams Detection Dataset (znsk27yk3h). While the original dataset focuses on MFS-specific fraud (bKash/Nagad), BanglaBarta provides:
1. **Broader coverage** of general smishing and spam
2. **Three-class taxonomy** (vs binary scam/ham)
3. **Different collection methodology** — telecom network samples vs Google Forms
4. **More recent** (2025 vs 2024)

### How to Download
1. Visit: https://data.mendeley.com/datasets/jfkfbw3gzh/2
2. Click "Download All" (118 KB zip)
3. Alternative: Use the download helper script

### Citation
```bibtex
@dataset{shahriyar2025bangalabarta,
  title={BangalaBarta: A Spam/Smishing SMS Dataset Bangla},
  author={Shahriyar, Md Farhan and Tanbhir, Gazi},
  year={2025},
  publisher={Mendeley Data},
  doi={10.17632/jfkfbw3zh.2}
}
```

---

## 2. GOVERNMENT WATCHDOG REPORT: TI-Bangladesh MFS Governance Study

### Overview
| Attribute | Detail |
|-----------|--------|
| **Title** | Governance Challenges in Mobile Financial Services Sector in Bangladesh |
| **Publisher** | Transparency International Bangladesh (TI-Bangladesh) |
| **Published** | May 2025 |
| **Type** | National survey + regulatory analysis |
| **URL** | https://www.ti-bangladesh.org/images/2025/report/mfs/Executive-Summary-Mobile-Financial-Services-Sector-En.pdf |

### Key Statistics for Your Paper

#### Fraud Victimization Rates (Table 3)
| Account Type | Victim of Fraud | Incurred Financial Loss |
|--------------|----------------|------------------------|
| **Individual account holders** | **6.3%** | **3.6%** |
| **Agent account holders** | **17.0%** | **8.7%** |
| **Merchant account holders** | **1.6%** | **1.4%** |

#### Financial Loss Ranges
| Account Type | Minimum Loss | Maximum Loss |
|--------------|-------------|--------------|
| Individual | BDT 300 | BDT 83,000 |
| Agent | BDT 200 | BDT 376,000 |
| Merchant | BDT 53 | BDT 45,000 |

#### Fraud Methods (Multiple Response)
| Method | Percentage |
|--------|-----------|
| Extorted through deceptive/false information | **52.6%** |
| Deception via phone calls or SMS | **42.1%** |
| Fraud through hacking | **12.3%** |

#### Complaint Behavior
| Behavior | Individual | Agent | Merchant |
|----------|-----------|-------|----------|
| Did NOT file complaint | **58.8%** | **60.9%** | **58.3%** |
| Filed complaint but no solution | 61.9% | - | - |
| Filed case/GD with police | **7.6%** | **27.4%** | **4.2%** |
| Reason: "no benefit" | 65.8% | 55.3% | 66.7% |
| Reason: "too time-consuming" | 30.1% | 25.9% | 25.0% |
| Reason: "fault was my own" | 23.3% | 15.7% | 16.7% |

#### MFS Market Share
| Provider | Individual | Agent | Merchant |
|----------|-----------|-------|----------|
| bKash | **84.4%** | **100%** | **92.4%** |
| Nagad | 30.9% | 60.4% | 4.2% |
| Rocket | 4.1% | 28.5% | 1.8% |

#### Agent Training Gaps
| Training Topic | % NEVER Trained |
|----------------|----------------|
| Hundi or money laundering | **78.6%** |
| Identifying suspicious transactions | **90.3%** |
| Countering terrorist financing | **90.3%** |

#### MFS Service Charges vs Banks
| Service | MFS Charge (BDT 25,000) | Bank Charge (BDT 25,000) |
|---------|------------------------|-------------------------|
| Cash Out | BDT 200-462.5 | BDT 0-29 |
| Inter-provider Transfer | BDT 125-375 | BDT 0-10 |
| Send Money | BDT 0-150 | BDT 0 |

**MFS charges are 15-50x higher than banks.**

#### Other Critical Statistics
- **14.3%** of personal account holders encountered difficulties using MFS
- **20.3%** lost money due to transfers to incorrect numbers
- **33.5%** reported network issues
- **6.4%** received remittances legally through MFS
- **59.0%** completed e-KYC through agents (privacy risk)
- **86.7%** of female account holders think charges are too high
- **58.4%** male vs **41.6%** female registered account holders
- Between 2011-2024: only **6 distributors** and **5,029 agent accounts** suspended for suspicious transactions
- STR/SAR submissions: **less than 0.001%** of total transactions

### Institutional Fraud: Nagad
- **Tk 645 crore** in e-money created without cash backing
- **Tk 1,711 crore** unauthorized withdrawals through 41 distributors
- **Tk 23.56 billion** unaccounted for in forensic audit
- Fake reporting portal disconnected from main server
- Former MD reinstated himself via email during legal vacuum

### Research Value
This report provides **the most comprehensive survey data** on MFS fraud in Bangladesh. It gives you:
1. **Prevalence rates** with sample size backing
2. **Financial loss quantification**
3. **Fraud method breakdown**
4. **Complaint behavior data**
5. **Agent training gap analysis**
6. **Market concentration statistics**
7. **Regulatory failure documentation**

---

## 3. CROWD-SOURCED DATA: Scam-Alert-BD (GitHub)

### Overview
| Attribute | Detail |
|-----------|--------|
| **Project** | Scam Alert BD |
| **URL** | https://github.com/mdnahidhossain0/Scam-Alert-BD |
| **Type** | Django-based scam detection platform |
| **Database** | SQLite (contains reported scams) |
| **Status** | Active open source project |

### Features
- Scam checker for phone numbers and bKash/Nagad IDs
- AI-powered scam message scanner
- URL scanner for phishing/malicious links
- Anonymous scam reporting
- Community stories from victims

### Potential Data
The SQLite database may contain:
- Reported scam phone numbers
- Fake bKash/Nagad agent IDs
- Scam URLs
- Scam message samples
- Community victim stories

### How to Access
```bash
git clone https://github.com/mdnahidhossain0/Scam-Alert-BD.git
cd Scam-Alert-BD
# Find SQLite database file
find . -name "*.db" -o -name "*.sqlite3"
# Extract data using sqlite3
sqlite3 db.sqlite3 ".tables"
sqlite3 db.sqlite3 "SELECT * FROM reported_scams;"
```

### Ethical Consideration
Contact the developer (@mdnahidhossain0) before using their data. The project is open source but the database contains user submissions that may not be intended for research use.

---

## 4. INSTITUTIONAL FRAUD: Nagad Case (2024-2025)

### Overview
The largest MFS fraud case in Bangladesh's history, uncovered after the August 2024 political transition.

### Timeline
| Date | Event |
|------|-------|
| March 2019 | Nagad launched without Bangladesh Bank approval |
| March 2020 | Interim approval granted (6 months, extended 9 times) |
| August 5, 2024 | Political transition, increased scrutiny |
| August 21, 2024 | Bangladesh Bank appoints administrator |
| November 18, 2024 | Investigation reveals Tk 645 crore e-money shortfall |
| February 3, 2025 | Criminal case filed at Motijheel Police Station |
| February 4, 2025 | Bangladesh Bank files fraud case against 24 individuals |
| May 7, 2025 | Supreme Court stay halts administrator |
| May 2025 | ACC files case for Tk 6.45 billion embezzlement |

### Key Findings
| Finding | Amount |
|---------|--------|
| E-money issued without cash backing | **Tk 645 crore** |
| Government allowance misappropriation | **Tk 1,711 crore** |
| Unauthorized distributors involved | **41** |
| Total unaccounted (forensic audit) | **Tk 23.56 billion** |
| Individuals sued | **24** (including former chairman, MD, directors) |
| Share transferred to British Virgin Islands | **70%** |

### Fraud Mechanisms
1. **Fake e-money creation:** Issued Tk 645 crore in electronic money without real currency reserves
2. **Fake reporting portal:** Disconnected from main server to mislead regulators
3. **Unauthorized distributors:** 41 distributors siphoned government allowances
4. **Ownership obfuscation:** 70% shares transferred to British Virgin Islands company
5. **Political capture:** Revenue-sharing agreement bypassed subsidiary requirement
6. **Identity appropriation:** Rebranded as Nagad Limited, registered trademarks in own name

### Regulatory Failures
- Operated for 5 years without formal approval
- Interim license extended 9 times (violated regulation)
- Bangladesh Bank failed to enforce subsidiary requirement
- Political influence blocked regulatory action
- Former BB officials joined Nagad/bKash within a year of retirement
- Regulatory officials allegedly received portion of gambling proceeds

### Sources
- TBS News (multiple articles, Jan-May 2025)
- The Daily Star (Feb 4, 2025)
- bdnews24 (May 31, 2025)
- Asia Post (June 4, 2025)
- Bangladesh Bank investigation report

---

## 5. RELATED ACADEMIC WORK

### Paper 1: Detecting Bengali Spam SMS Using RNN (2020)
- **Authors:** Md. Mohsin Uddin et al.
- **Institution:** East West University (your university!)
- **Journal:** Journal of Communications, Vol 15, No 4
- **DOI:** 10.12720/jcm.15.4.325-331
- **Finding:** LSTM and GRU achieved 99% accuracy on Bangla spam detection
- **Significance:** First to apply deep learning for Bangla spam SMS
- **URL:** https://www.jocm.us/show-238-1530-1.html

### Paper 2: Exploring BERT and ELMo for Bangla Spam SMS (2024)
- **Authors:** Multiple (from ResearchGate)
- **Focus:** BanglaBERT and ELMo embeddings for spam detection
- **URL:** https://www.researchgate.net/publication/378529076

### Paper 3: Combating Mobile Financial Fraud in Bangladesh (2025)
- **Focus:** NLP + ML approaches for MFS fraud
- **Claim:** ~94% accuracy achieved
- **URL:** https://www.researchgate.net/publication/395202782

### Paper 4: Cyber Fraud in Bangladesh's Digital Financial Ecosystem (2025)
- **Focus:** Uses 2025 Standard Chartered Bank OTP scam as case study
- **Approach:** Multi-actor responsibility model
- **Findings:** Systemic failure across banks, MFS, regulators, users
- **URL:** https://rsisinternational.org/journals/ijrsi/view/cyber-fraud-in-bangladesh-s-digital-financial-ecosystem-tracing-responsibility-across-banks-mobile-financial-services-and-end-users

---

## 6. SUMMARY: ALL DISCOVERED DATA SOURCES

| # | Source | Type | Size/Scope | Access |
|---|--------|------|-----------|--------|
| 1 | Financial Scams Detection Dataset | Dataset (Mendeley) | Labeled EN+BN messages | Download (CC-BY) |
| 2 | **BanglaBarta Dataset** | **Dataset (Mendeley)** | **2,772 Bangla SMS (3 classes)** | **Download (CC BY-NC-SA)** |
| 3 | **TI-Bangladesh Report** | **Government Survey** | **National MFS governance study** | **Public PDF** |
| 4 | **Scam-Alert-BD** | **GitHub + Database** | **Crowd-sourced scam reports** | **Open source** |
| 5 | **Nagad Fraud Case** | **News + Court docs** | **Tk 1,711 crore institutional fraud** | **Public records** |
| 6 | @LGPaymentgateway (Telegram) | Public channel | 1.09K subs, payment gateway | Scrapable |
| 7 | @ag4566 (Telegram) | Public channel | OKEXPAY, bKash/Nagad processing | Scrapable |
| 8 | CIRT Bangladesh | Government advisories | Security alerts | Website |
| 9 | BRAC University Thesis | Academic | bKash fraud risk management | Repository |
| 10 | East West University Paper | Academic | Bangla spam RNN detection | Journal |

---

## 7. RECOMMENDED CITATIONS FOR YOUR PAPER

### For Introduction/Background
> "According to a national survey by Transparency International Bangladesh, 6.3% of individual MFS account holders and 17.0% of agents have fallen victim to fraud, with financial losses ranging from BDT 300 to BDT 376,000 [cite TI-Bangladesh 2025]. Despite this, 58.8% of victims never filed complaints, primarily believing it would yield no benefit (65.8%) [cite]. The Bangladesh Bank has revealed institutional-scale fraud at Nagad, involving Tk 1,711 crore (~$1.4B USD) in misappropriated government social security allowances through 41 unauthorized distributors [cite TBS News 2025]."

### For Related Work
> "Prior work on Bangla spam detection includes Uddin et al. [cite] who applied LSTM and GRU to Bengali SMS classification, achieving 99% accuracy. However, these studies focused on generic spam rather than MFS-specific scam ecosystems. Shahriyar and Tanbhir [cite BanglaBarta 2025] released a 2,772-message dataset for smishing detection in Bangla, but it lacks MFS-specific categories and infrastructure analysis."

---

## 8. NEXT STEPS

### Immediate (This Week)
1. **Download BanglaBarta dataset** from Mendeley (https://data.mendeley.com/datasets/jfkfbw3gzh/2)
2. **Download TI-Bangladesh report** (https://www.ti-bangladesh.org/images/2025/report/mfs/Executive-Summary-Mobile-Financial-Services-Sector-En.pdf)
3. **Clone Scam-Alert-BD** and examine database (git clone https://github.com/mdnahidhossain0/Scam-Alert-BD.git)
4. **Download both Mendeley datasets** and run through processing pipeline

### Short Term (Next 2 Weeks)
5. **Read TI-Bangladesh report end-to-end** — extract all statistics for your paper
6. **Contact Scam-Alert-BD developer** for permission to use database
7. **Scrape Telegram channels** (@LGPaymentgateway, @ag4566) using built scraper
8. **Search for Facebook pages** using the search patterns documented

### Medium Term (Next Month)
9. **Merge both datasets** (Financial Scams + BanglaBarta) for combined analysis
10. **Build prevalence statistics** using TI-Bangladesh survey data
11. **Document Nagad case** as institutional fraud example
12. **Write Background section** with all these new statistics

---

*Report generated: May 2026*
*Sources: Mendeley Data, TI-Bangladesh, TBS News, The Daily Star, GitHub, ResearchGate, Academia.edu*
