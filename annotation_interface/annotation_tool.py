#!/usr/bin/env python3
"""
Annotation Interface for MFS Scam Taxonomy
- 7-category codebook with examples
- Inter-annotator agreement tracking
- Adjudication workflow

Usage:
    python annotation_interface.py --setup --dataset messages.csv
    python annotation_interface.py --adjudicate --annotations annotator1.csv annotator2.csv

Generates HTML annotation interface + analysis scripts
"""

import argparse
import csv
import json
import os
from datetime import datetime
from collections import Counter

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("ERROR: pip install pandas numpy")
    raise


# ============ TAXONOMY CODEBOOK ============

TAXONOMY = {
    "categories": [
        {
            "id": 1,
            "name": "Account Compromise",
            "description": "Messages claiming the target's account is suspended, locked, or accessed by a third party. Requests PIN or OTP.",
            "examples_en": [
                "Your bKash account has been suspended. Send OTP to reactivate.",
                "Unauthorized login detected. Reply with your PIN to secure account.",
                "Your Nagad account will be blocked. Enter verification code:"
            ],
            "examples_bn": [
                "আপনার বিকাশ অ্যাকাউন্ট স্থগিত করা হয়েছে। OTP পাঠিয়ে পুনরায় সক্রিয় করুন।",
                "অননুমোদিত লগইন সনাক্ত হয়েছে। অ্যাকাউন্ট সুরক্ষিত করতে আপনার PIN উত্তর দিন।"
            ],
            "key_indicators": ["suspended", "blocked", "locked", "unauthorized", "verification", "reactivate", "OTP", "PIN"],
            "color": "#e74c3c"
        },
        {
            "id": 2,
            "name": "Fake Promotional Offer",
            "description": "Falsely claims cashback, bonus credit, or special offer from bKash/Nagad. Asks target to 'activate' by sending money or code.",
            "examples_en": [
                "Get 500 BDT cashback! Send money to activate bonus offer.",
                "bKash Eid offer: Send 1000 get 2000! Limited time only!",
                "Congratulations! You are selected for Nagad bonus program."
            ],
            "examples_bn": [
                "৫০০ টাকা ক্যাশব্যাক পান! বোনাস অফার সক্রিয় করতে টাকা পাঠান।",
                "বিকাশ ঈদ অফার: ১০০০ পাঠান ২০০০ পান! সীমিত সময়ের জন্য!"
            ],
            "key_indicators": ["cashback", "bonus", "offer", "activate", "promo", "free money", "double", "free"],
            "color": "#f39c12"
        },
        {
            "id": 3,
            "name": "Lottery / Prize Scam",
            "description": "Claims target has won a prize. Requests processing fee or personal details.",
            "examples_en": [
                "You have won 100,000 BDT! Call to claim your prize.",
                "Lucky draw winner! Your mobile number won 50000 taka.",
                "Nagad lottery: You are the 1000th customer winner!"
            ],
            "examples_bn": [
                "আপনি ১০০,০০০ টাকা জিতেছেন! পুরস্কার দাবি করতে কল করুন।",
                "লাকি ড্র বিজয়ী! আপনার মোবাইল নম্বর ৫০,০০০ টাকা জিতেছে।"
            ],
            "key_indicators": ["won", "winner", "lottery", "prize", "lucky draw", "claim", "processing fee"],
            "color": "#9b59b6"
        },
        {
            "id": 4,
            "name": "Loan / Job Scam",
            "description": "Offers easy loans or high-paying jobs contingent on upfront fee via MFS.",
            "examples_en": [
                "Get instant loan up to 50000 BDT. Pay 500 processing fee via bKash.",
                "High paying job abroad! Deposit 2000 BDT for registration.",
                "Easy personal loan, no documents needed. Send advance payment."
            ],
            "examples_bn": [
                "তাৎক্ষণিক ঋণ ৫০,০০০ টাকা পর্যন্ত। বিকাশের মাধ্যমে ৫০০ প্রক্রিয়াকরণ ফি দিন।",
                "বিদেশে উচ্চ বেতনের চাকরি! রেজিস্ট্রেশনের জন্য ২০০০ টাকা জমা দিন।"
            ],
            "key_indicators": ["loan", "job", "employment", "salary", "processing fee", "registration fee", "advance payment"],
            "color": "#3498db"
        },
        {
            "id": 5,
            "name": "Impersonation",
            "description": "Impersonates a known individual (friend, relative, employer) in distress requesting urgent money transfer.",
            "examples_en": [
                "It's me, your uncle. Emergency, send 5000 BDT quickly to this number.",
                "Boss here. Send money to this bKash number immediately for office work.",
                "I'm stuck at the border, send money urgently via Nagad."
            ],
            "examples_bn": [
                "এটি আমি, তোমার চাচা। জরুরী, দ্রুত এই নম্বরে ৫০০০ টাকা পাঠাও।",
                "বস এখানে। অফিসের কাজের জন্য দ্রুত এই বিকাশ নম্বরে টাকা পাঠাও।"
            ],
            "key_indicators": ["emergency", "urgent", "me", "your", "stuck", "help", "relative", "boss", "friend"],
            "color": "#1abc9c"
        },
        {
            "id": 6,
            "name": "Phishing Link",
            "description": "Contains a URL impersonating official MFS portal or bank to harvest credentials.",
            "examples_en": [
                "Verify your account: https://bkash-login-verify.tk/secure",
                "Update your Nagad KYC: http://nagad-update.xyz/login",
                "Click to confirm transaction: https://secure-dbbl.tk/verify"
            ],
            "examples_bn": [
                "আপনার অ্যাকাউন্ট যাচাই করুন: https://bkash-login-verify.tk/secure",
                "আপনার নগদ KYC আপডেট করুন: http://nagad-update.xyz/login"
            ],
            "key_indicators": ["http", "click", "link", "verify", "login", "update", "confirm", ".tk", ".xyz"],
            "color": "#e67e22"
        },
        {
            "id": 7,
            "name": "Legitimate (Ham)",
            "description": "Genuine transactional messages from MFS providers.",
            "examples_en": [
                "Cash In Tk 500.00 from 01XXXXXXXXX successful. Balance: Tk 2,450.00",
                "You have received Tk 1,000.00 from Unknown Number. Balance: Tk 5,200",
                "Your bKash PIN has been changed successfully."
            ],
            "examples_bn": [
                "ক্যাশ ইন টাকা ৫০০.০০ সফল। ব্যালেন্স: টাকা ২,৪৫০.০০",
                "আপনি টাকা ১,০০০.০০ পেয়েছেন। ব্যালেন্স: টাকা ৫,২০০"
            ],
            "key_indicators": ["successful", "received", "balance", "txid", "transaction id", "official"],
            "color": "#27ae60"
        }
    ]
}


def generate_annotation_html(output_path, sample_messages=None):
    """Generate HTML annotation interface with the 7-category codebook."""

    categories_html = ""
    for cat in TAXONOMY["categories"]:
        examples_en = "<br>".join(f"  - {ex}" for ex in cat["examples_en"])
        examples_bn = "<br>".join(f"  - {ex}" for ex in cat["examples_bn"]) if cat["examples_bn"] else ""
        indicators = ", ".join(cat["key_indicators"])

        categories_html += f"""
        <div class="category-card" style="border-left: 5px solid {cat['color']};" onclick="selectCategory({cat['id']})">
            <div class="cat-header">
                <span class="cat-id" style="background: {cat['color']};">{cat['id']}</span>
                <span class="cat-name">{cat['name']}</span>
            </div>
            <div class="cat-desc">{cat['description']}</div>
            <div class="cat-indicators"><strong>Key indicators:</strong> {indicators}</div>
            <div class="cat-examples">
                <div class="examples-en">{examples_en}</div>
                <div class="examples-bn">{examples_bn}</div>
            </div>
        </div>
        """

    # Sample messages table
    messages_html = ""
    if sample_messages:
        for i, msg in enumerate(sample_messages[:50]):  # First 50
            messages_html += f"""
            <tr data-msg-id="{i}">
                <td>{i+1}</td>
                <td class="msg-text">{msg.get('message', msg.get('text', ''))}</td>
                <td class="annotation-cell">
                    <select class="cat-select" onchange="updateAnnotation({i}, this.value)">
                        <option value="">-- Select --</option>
                        {''.join(f'<option value="{c["id"]}">{c["id"]}. {c["name"]}</option>' for c in TAXONOMY["categories"])}
                        <option value="skip">Skip / Unclear</option>
                    </select>
                </td>
                <td><input type="text" class="notes-input" placeholder="Notes..." onchange="updateNotes({i}, this.value)"></td>
            </tr>
            """

    css = """
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { font-family: 'Segoe UI', Tahoma, sans-serif; display: flex; height: 100vh; }
    .sidebar { width: 40%; background: #f8f9fa; padding: 20px; overflow-y: auto; border-right: 2px solid #ddd; }
    .sidebar h2 { margin-bottom: 15px; color: #333; }
    .category-card { background: white; padding: 15px; margin-bottom: 12px; border-radius: 8px; cursor: pointer; transition: all 0.2s; }
    .category-card:hover { transform: translateX(5px); box-shadow: 0 2px 8px rgba(0,0,0,0.1); }
    .category-card.active { background: #e8f4fd; border: 2px solid #3498db; }
    .cat-header { display: flex; align-items: center; margin-bottom: 8px; }
    .cat-id { width: 28px; height: 28px; border-radius: 50%; color: white; display: flex; align-items: center; justify-content: center; font-weight: bold; margin-right: 10px; }
    .cat-name { font-weight: 600; font-size: 15px; }
    .cat-desc { font-size: 13px; color: #555; margin-bottom: 8px; line-height: 1.4; }
    .cat-indicators { font-size: 12px; color: #777; margin-bottom: 8px; }
    .cat-examples { font-size: 12px; color: #666; background: #f5f5f5; padding: 8px; border-radius: 4px; }
    .examples-bn { color: #006847; margin-top: 5px; }
    .main { flex: 1; padding: 20px; overflow-y: auto; }
    .main h2 { margin-bottom: 15px; }
    .progress-bar { width: 100%; height: 8px; background: #e0e0e0; border-radius: 4px; margin-bottom: 15px; }
    .progress-fill { height: 100%; background: linear-gradient(90deg, #e31e24, #ff6b6b); border-radius: 4px; width: 0%; transition: width 0.3s; }
    table { width: 100%; border-collapse: collapse; font-size: 14px; }
    th { background: #333; color: white; padding: 12px; text-align: left; position: sticky; top: 0; }
    td { padding: 10px; border-bottom: 1px solid #eee; }
    .msg-text { max-width: 400px; word-wrap: break-word; font-family: monospace; background: #f9f9f9; padding: 8px; border-radius: 4px; }
    .cat-select { padding: 6px 12px; border-radius: 4px; border: 1px solid #ddd; font-size: 13px; cursor: pointer; }
    .notes-input { padding: 6px; border: 1px solid #ddd; border-radius: 4px; width: 100%; font-size: 12px; }
    tr.annotated { background: #e8f5e9; }
    .controls { position: fixed; bottom: 20px; right: 20px; display: flex; gap: 10px; }
    .btn { padding: 12px 24px; border: none; border-radius: 25px; cursor: pointer; font-size: 14px; font-weight: 600; }
    .btn-primary { background: linear-gradient(135deg, #e31e24, #ff6b6b); color: white; }
    .btn-secondary { background: #333; color: white; }
    .stats { position: fixed; top: 20px; right: 20px; background: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); font-size: 13px; }
    .shortcut { display: inline-block; background: #eee; padding: 2px 6px; border-radius: 3px; font-size: 11px; }
    """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><title>MFS Scam Annotation Interface</title>
<style>{css}</style></head>
<body>
<div class="sidebar">
    <h2>Taxonomy Codebook <span class="shortcut">Press 1-7 to select</span></h2>
    {categories_html}
    <div style="margin-top: 20px; padding: 15px; background: #fff3cd; border-radius: 8px; font-size: 13px;">
        <strong>Instructions:</strong>
        <ol style="margin-left: 15px; margin-top: 5px;">
            <li>Read each message carefully</li>
            <li>Select the best matching category</li>
            <li>Use "Skip" for ambiguous messages</li>
            <li>Add notes for borderline cases</li>
        </ol>
    </div>
</div>
<div class="main">
    <h2>Messages to Annotate</h2>
    <div class="progress-bar"><div class="progress-fill" id="progressBar"></div></div>
    <table>
        <thead><tr><th>#</th><th>Message</th><th>Category</th><th>Notes</th></tr></thead>
        <tbody id="messageTable">{messages_html}</tbody>
    </table>
</div>
<div class="stats" id="statsPanel">
    <strong>Progress</strong><br>
    Annotated: <span id="annotatedCount">0</span>/<span id="totalCount">{len(sample_messages) if sample_messages else 0}</span><br>
    Remaining: <span id="remainingCount">{len(sample_messages) if sample_messages else 0}</span>
</div>
<div class="controls">
    <button class="btn btn-secondary" onclick="exportAnnotations()">Export CSV</button>
    <button class="btn btn-primary" onclick="saveAnnotations()">Save Progress</button>
</div>
<script>
const annotations = {{}};
let selectedCategory = null;

function selectCategory(catId) {{
    selectedCategory = catId;
    document.querySelectorAll('.category-card').forEach(c => c.classList.remove('active'));
    event.currentTarget.classList.add('active');
}}

function updateAnnotation(msgId, category) {{
    annotations[msgId] = annotations[msgId] || {{}};
    annotations[msgId].category = category;
    annotations[msgId].timestamp = new Date().toISOString();
    const row = document.querySelector(`tr[data-msg-id="${{msgId}}"]`);
    if (category && category !== 'skip') row.classList.add('annotated');
    updateProgress();
}}

function updateNotes(msgId, notes) {{
    annotations[msgId] = annotations[msgId] || {{}};
    annotations[msgId].notes = notes;
}}

function updateProgress() {{
    const total = document.querySelectorAll('#messageTable tr').length;
    const annotated = Object.values(annotations).filter(a => a.category && a.category !== 'skip').length;
    document.getElementById('annotatedCount').textContent = annotated;
    document.getElementById('remainingCount').textContent = total - annotated;
    document.getElementById('progressBar').style.width = (annotated / total * 100) + '%';
    document.getElementById('totalCount').textContent = total;
}}

function exportAnnotations() {{
    const rows = [['msg_id', 'category_id', 'category_name', 'notes', 'timestamp']];
    for (const [msgId, ann] of Object.entries(annotations)) {{
        if (ann.category && ann.category !== 'skip') {{
            const catNames = {{1:'Account Compromise',2:'Fake Promo',3:'Lottery',4:'Loan/Job',5:'Impersonation',6:'Phishing Link',7:'Legitimate'}};
            rows.push([msgId, ann.category, catNames[ann.category]||'', ann.notes||'', ann.timestamp||'']);
        }}
    }}
    const csv = rows.map(r => r.join(',')).join('\n');
    const blob = new Blob([csv], {{type: 'text/csv'}});
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'annotations_' + new Date().toISOString().slice(0,10) + '.csv';
    a.click();
}}

function saveAnnotations() {{
    localStorage.setItem('mfs_annotations', JSON.stringify(annotations));
    alert('Progress saved to browser localStorage!');
}}

// Keyboard shortcuts
document.addEventListener('keydown', (e) => {{
    if (e.key >= '1' && e.key <= '7') {{
        const catId = parseInt(e.key);
        document.querySelector(`.category-card:nth-child(${{catId}})`).click();
    }}
}});

// Load saved annotations
const saved = localStorage.getItem('mfs_annotations');
if (saved) Object.assign(annotations, JSON.parse(saved));
updateProgress();
</script>
</body></html>"""

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"[+] Annotation interface: {output_path}")
    return output_path


def compute_inter_annotator_agreement(annotator1_csv, annotator2_csv, output_path=None):
    """Compute Cohen's Kappa and category-level agreement."""
    df1 = pd.read_csv(annotator1_csv)
    df2 = pd.read_csv(annotator2_csv)

    # Merge on message_id
    merged = pd.merge(df1, df2, on='msg_id', suffixes=('_a1', '_a2'))

    # Overall agreement
    agreement = (merged['category_id_a1'] == merged['category_id_a2']).mean()

    # Category-level agreement
    cats = sorted(merged['category_id_a1'].unique())
    cat_agreement = {}
    for cat in cats:
        subset = merged[merged['category_id_a1'] == cat]
        cat_agreement[int(cat)] = {
            'count': len(subset),
            'agreement': (subset['category_id_a1'] == subset['category_id_a2']).mean()
        }

    # Cohen's Kappa
    try:
        from sklearn.metrics import cohen_kappa_score
        kappa = cohen_kappa_score(merged['category_id_a1'], merged['category_id_a2'])
    except ImportError:
        # Manual calculation
        kappa = compute_kappa_manual(merged['category_id_a1'], merged['category_id_a2'])

    report = {
        'generated_at': datetime.now().isoformat(),
        'total_annotated': len(merged),
        'overall_agreement': round(agreement, 4),
        'cohens_kappa': round(kappa, 4),
        'kappa_interpretation': interpret_kappa(kappa),
        'category_agreement': cat_agreement,
        'disagreement_cases': []
    }

    # Log disagreements
    disagreements = merged[merged['category_id_a1'] != merged['category_id_a2']]
    for _, row in disagreements.head(20).iterrows():
        report['disagreement_cases'].append({
            'msg_id': int(row['msg_id']),
            'annotator1': int(row['category_id_a1']),
            'annotator2': int(row['category_id_a2'])
        })

    if output_path:
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)

    print("\n" + "="*60)
    print("INTER-ANNOTATOR AGREEMENT REPORT")
    print("="*60)
    print(f"Total annotated:        {report['total_annotated']}")
    print(f"Overall agreement:      {report['overall_agreement']:.2%}")
    print(f"Cohen's Kappa:          {report['cohens_kappa']:.4f}")
    print(f"Interpretation:         {report['kappa_interpretation']}")
    print(f"\nCategory-level agreement:")
    for cat, stats in report['category_agreement'].items():
        cat_name = [c['name'] for c in TAXONOMY['categories'] if c['id'] == cat]
        name = cat_name[0] if cat_name else 'Unknown'
        print(f"  [{cat}] {name}: {stats['agreement']:.2%} ({stats['count']} samples)")
    print("="*60)

    return report


def compute_kappa_manual(a1, a2):
    """Manual Cohen's Kappa calculation."""
    n = len(a1)
    observed = sum(x == y for x, y in zip(a1, a2)) / n

    # Expected agreement
    cats = set(list(a1.unique()) + list(a2.unique()))
    expected = 0
    for cat in cats:
        p1 = sum(a1 == cat) / n
        p2 = sum(a2 == cat) / n
        expected += p1 * p2

    if expected == 1:
        return 1.0

    return (observed - expected) / (1 - expected)


def interpret_kappa(kappa):
    if kappa < 0: return "Poor agreement"
    elif kappa < 0.20: return "Slight agreement"
    elif kappa < 0.40: return "Fair agreement"
    elif kappa < 0.60: return "Moderate agreement"
    elif kappa < 0.80: return "Substantial agreement"
    else: return "Almost perfect agreement"


def main():
    parser = argparse.ArgumentParser(description="MFS Scam Annotation Interface")
    parser.add_argument("--setup", action="store_true", help="Generate annotation HTML")
    parser.add_argument("--dataset", help="Path to message dataset CSV")
    parser.add_argument("--output", default="./annotation", help="Output directory")
    parser.add_argument("--agreement", action="store_true", help="Compute IAA")
    parser.add_argument("--annotations", nargs=2, help="Two annotator CSV files")
    parser.add_argument("--report", help="Output report JSON path")

    args = parser.parse_args()
    os.makedirs(args.output, exist_ok=True)

    if args.setup:
        messages = None
        if args.dataset:
            df = pd.read_csv(args.dataset)
            msg_col = [c for c in df.columns if 'message' in c.lower() or 'text' in c.lower()][0]
            messages = df.head(100).to_dict('records')

        html_path = os.path.join(args.output, "annotation_interface.html")
        generate_annotation_html(html_path, messages)

        # Also save codebook as JSON
        codebook_path = os.path.join(args.output, "taxonomy_codebook.json")
        with open(codebook_path, 'w', encoding='utf-8') as f:
            json.dump(TAXONOMY, f, indent=2, ensure_ascii=False)
        print(f"[+] Codebook JSON: {codebook_path}")
        print(f"[*] Open {html_path} in browser to start annotating")

    if args.agreement and args.annotations:
        compute_inter_annotator_agreement(
            args.annotations[0], args.annotations[1],
            output_path=args.report
        )


if __name__ == "__main__":
    main()
