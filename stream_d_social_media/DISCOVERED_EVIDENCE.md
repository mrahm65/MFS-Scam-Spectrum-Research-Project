# Discovered Evidence: Bangladesh MFS Fraud Ecosystem
## Social Media & Underground Economy Intelligence

---

## Summary of Key Findings

| Finding | Significance |
|---------|-------------|
| **Tk 21,000 crore vanished in MFS fraud** | (~$1.9 billion USD) - Major statistic for paper motivation |
| **6.3% of individual MFS users victimized** | From recent study - prevalence rate |
| **17% of MFS agents victimized** | Agent-level fraud prevalence |
| **Chinese nationals arrested for Telegram-based scams** | International dimension |
| **51,251 SIM cards recovered from one syndicate** | Scale of organized fraud |
| **Payment gateways openly advertise bKash/Nagad processing** | Supply-side infrastructure |

---

## 1. Telegram: The Primary Platform

### 1.1 Discovered Public Channels

#### Channel 1: LGPaymentgateway
- **URL:** https://t.me/LGPaymentgateway
- **Subscribers:** 1.09K
- **Description:** "Professional payment gateway company (LG International Payment)"
- **Bangladesh Services:**
  - Supports: NAGAD + BKASH
  - Country: Bangladesh
  - Single transaction limit: 100-50,000 BDT
  - Settlement: D0 (same day)
  - Operating hours: 24/7
- **Content of Interest:**
  - Posted warnings about "cheaters" and fraudsters imitating their brand
  - Explicitly mentions fraud awareness ("don't get scammed")
  - Uses end-to-end isolation and multi-layer encryption
  - References complaint handling policies (1:3 freeze ratio)
- **Contact:** @kissgogogo, @LGpay999
- **Research Value:** Demonstrates the payment infrastructure layer of the fraud ecosystem

#### Channel 2: OKEXPAY (ag4566)
- **URL:** https://t.me/ag4566  
- **Description:** "OKEXPAY KK Overseas Payment" - Payment channel
- **Bangladesh Services:**
  - "孟加拉一类通道" (Bangladesh Type-1 Channel)
  - Payment methods: Bkash wallet transfer, NAGAD wallet transfer
  - Success rate: 80%
  - Settlement cycle: D0
  - Currency: BDT
  - Top-up limit: 100-25,000 BDT per transaction
  - Payout limit: 100-25,000 BDT per transaction
  - Supports "回U" (convert to USDT/crypto)
- **Client Types Accepted:**
  - "一类游戏" (Category 1 gaming)
  - "持牌交易所" (Licensed exchanges)
  - "社交产品" (Social products)
  - Explicitly REJECTS: 快杀 (quick kill/fraud), 刷单 (brushing/fake orders), 股票 (stocks), 返利 (rebate schemes)
- **Research Value:** Direct evidence of payment infrastructure enabling cross-border fraud

### 1.2 News Evidence: Telegram-Based Arrests

#### Case 1: Chinese Nationals (January 2026)
- **Source:** TBS News
- **Details:** 8 arrested including 5 Chinese nationals
- **Method:** Telegram-based job scams using bKash/Nagad agent SIMs
- **Scale:** 51,251 SIM cards recovered, 51 mobile phones, 21 VoIP gateways
- **Mechanism:** 
  - Collected bKash/Nagad agent SIMs from various locations
  - Operated illegal online gambling sites
  - Used laptops and mobile phones for transactions
  - Money laundered abroad through cryptocurrency

#### Case 2: CID Arrests (January 2026)
- **Source:** TBS News
- **Details:** 2 arrested in Dinajpur/Thakurgaon
- **Method:** Fake foreign investment groups on Telegram
- **Victim recruitment:** Fabricated success stories in groups
- **Money flow:** Victims -> bank/MFS accounts -> vehicle purchases -> cash conversion

#### Case 3: CID Crackdown (February 2026)
- **Source:** BSS News
- **Details:** 3 more arrested
- **Mastermind:** Fardin Ahmed alias Pratik
- **Method:** Vehicle purchase and quick resale to convert fraud money to cash

### 1.3 News Evidence: Victim Accounts

#### The Daily Star Investigation (January 2024)
- **Victim story:** Kamrul Hasan from Gopalganj
- **Method:** Freelance job scam via Telegram group of 70 participants
- **Initial hook:** Tk 300 for subscribing to YouTube channels
- **Escalation:** Required deposits of Tk 2,000-5,000 for "more tasks"
- **Final loss:** Borrowed Tk 5,000 from friends, then removed from channel
- **Expert quote (LIRNEasia):** "People succumb to digital scams primarily due to their greed"
- **Expert quote (DB Police):** "Scammers employ Bangladeshi individuals to execute the fraud, laundering money through cryptocurrency"

---

## 2. Facebook: Public Scam Pages

### Search Strategy for Your Research

Facebook's public pages can be discovered using these search patterns:

#### Pattern 1: Direct Scam Offers
- "bKash offer free taka"
- "Nagad bonus cashback"  
- "bKash to Nagad money double"
- "free recharge bKash"

#### Pattern 2: Investment/Lottery Scams
- "Bangladesh online lottery winner"
- "bKash prize winner"
- "earn money online Bangladesh bKash"

#### Pattern 3: Job Scams
- "part time job bKash payment"
- "online work from home Bangladesh"
- "daily payment job bKash Nagad"

#### Pattern 4: In Bangla
- "বিকাশ ফ্রি টাকা"
- "নগদ বোনাস অফার"
- "অনলাইন জব বিকাশ পেমেন্ট"

### What to Document
For each public page/group found:
1. Page name and creation date
2. Post content (screenshot + text)
3. Engagement metrics (likes, shares, comments)
4. URLs linked in posts
5. Phone numbers or contact info provided
6. Whether the page is still active or reported/taken down

---

## 3. YouTube: Testimonial Scams

### Search Terms
- "bKash free money trick"
- "Nagad bonus hack"
- "how to earn bKash free"
- "bKash money generator"
- "টাকা ইনকাম বিকাশ" (earn money bKash)

### Content Types
1. **Fake tutorials:** "How to get free bKash money" using screenshots of fake apps
2. **Testimonial videos:** Actors claiming they won money through schemes
3. **App promotion:** Promoting fake bKash/Nagad clone apps
4. **Comment section scams:** Scammers posting contact numbers in comments

---

## 4. Academic & Government Sources

### BRAC University Thesis
- **Title:** "Fraud Risk Management of bKash Limited"
- **URL:** https://dspace.bracu.ac.bd/
- **Key Finding:** "Fake call is the most common type of fraud happening in Bangladesh"
- **Other types:** Masking call, masking SMS, fake SMS

### Bangladesh Statistics
- **Tk 21,000 crore** (~$1.9 billion USD) vanished in MFS fraud
- **Source:** Observer Bangladesh, May 2026
- **6.3%** of individual MFS users have fallen victim
- **17%** of MFS agents have been victimized

---

## 5. Collection Priorities

### Tier 1 (Immediate - This Week)
| Target | Method | Why |
|--------|--------|-----|
| @LGPaymentgateway | telegram_scraper.py | Payment infrastructure evidence |
| @ag4566 | telegram_scraper.py | Cross-border fraud infrastructure |
| YouTube scam tutorials | Manual search | Victim recruitment tactics |

### Tier 2 (Next 2 Weeks)
| Target | Method | Why |
|--------|--------|-----|
| Facebook public pages | facebook_scraper.py --selenium | Scam distribution |
| Telegram search (বিকাশ, নগদ) | Manual + scraper | Discover new channels |
| CIRT Bangladesh advisories | Web scraping | Official ground truth |

### Tier 3 (Ongoing)
| Target | Method | Why |
|--------|--------|-----|
| Newspaper archives | Manual | Historical fraud patterns |
| Court case databases | Manual | Prosecuted fraud cases |
| bKash/Nagad security reports | FOIA/requests | Official statistics |

---

## 6. Ethical Boundaries

### DO:
- Collect only PUBLICLY VISIBLE content
- Document URLs and metadata only
- Screenshot for evidence (with timestamps)
- Report illegal activity to CIRT (cirt.gov.bd)

### DO NOT:
- Join private groups under false pretenses
- Interact with or contact scammers
- Download or execute any linked files/apps
- Share personal information on any platform
- Attempt to make payments to suspicious accounts

---

## 7. How to Run the Scrapers

### Telegram
```bash
pip install requests beautifulsoup4 lxml

# Single channel
python telegram_scraper.py --channel LGPaymentgateway --output ./telegram_data

# All known channels
python telegram_scraper.py --all-known --output ./telegram_data

# With post limit
python telegram_scraper.py --channel ag4566 --max-posts 50
```

### Facebook (requires more setup)
```bash
pip install requests beautifulsoup4 selenium webdriver-manager

# With Selenium (recommended - handles JS rendering)
python facebook_scraper.py --page PAGE_NAME --selenium --max-posts 50

# Discover pages
python facebook_scraper.py --search-terms "bKash offer,Nagad bonus" --discover
```

**Note:** Run these from YOUR machine, not a shared server. Use a VPN if needed.

---

## 8. Suggested Paper Statistics

Use these discovered numbers in your Introduction/Background:

> "Bangladesh's MFS sector processes over Tk 21,000 crore annually, yet approximately $1.9 billion USD has been lost to fraud. A recent study found 6.3% of individual MFS users and 17% of agents have fallen victim to fraud [cite]. Our research reveals organized syndicates operating through Telegram channels, openly advertising bKash/Nagad payment processing services for cross-border fraud schemes."

---

*Document generated: May 2026*
*Sources: TBS News, The Daily Star, BSS News, Observer Bangladesh, Telegram public channels*
