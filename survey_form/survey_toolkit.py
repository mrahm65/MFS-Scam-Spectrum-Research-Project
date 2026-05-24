#!/usr/bin/env python3
"""
Survey Form Generator & Data Processing for MFS Scam Susceptibility Study
Generates HTML survey form + JSON schema, processes responses
"""

import argparse
import csv
import json
import os
import re
from datetime import datetime
from collections import Counter

try:
    import pandas as pd
    import numpy as np
except ImportError:
    print("ERROR: pip install pandas numpy")
    raise


# Survey instrument definition
SURVEY_SECTIONS = [
    {
        "section_id": "A",
        "title_en": "Section A: Demographics",
        "title_bn": "অনুচ্ছেদ ক: জনসংখ্যাতাত্ত্বিক তথ্য",
        "questions": [
            {"id": "A1", "type": "radio", "text_en": "What is your age group?", "text_bn": "আপনার বয়সের শ্রেণী কি?", "options": ["18-24", "25-34", "35-44", "45-54", "55+"], "required": True},
            {"id": "A2", "type": "radio", "text_en": "What is your gender?", "text_bn": "আপনার লিঙ্গ কি?", "options": ["Male", "Female", "Other", "Prefer not to say"], "required": True},
            {"id": "A3", "type": "radio", "text_en": "Highest education level?", "text_bn": "সর্বোচ্চ শিক্ষাগত যোগ্যতা?", "options": ["Primary or below", "Secondary", "Higher Secondary", "Bachelor's", "Master's+"], "required": True},
            {"id": "A4", "type": "radio", "text_en": "Where do you live?", "text_bn": "কোথায় থাকেন?", "options": ["Urban", "Semi-urban", "Rural"], "required": True},
            {"id": "A5", "type": "radio", "text_en": "Occupation?", "text_bn": "পেশা?", "options": ["Student", "Private employee", "Govt employee", "Business", "Unemployed", "Retired", "Other"], "required": True},
            {"id": "A6", "type": "radio", "text_en": "Monthly income?", "text_bn": "মাসিক আয়?", "options": ["No income", "<10k BDT", "10-30k", "30-60k", "60-100k", ">100k", "Prefer not to say"], "required": True},
        ]
    },
    {
        "section_id": "B",
        "title_en": "Section B: MFS Usage",
        "title_bn": "অনুচ্ছেদ খ: এমএফএস ব্যবহার",
        "questions": [
            {"id": "B1", "type": "checkbox", "text_en": "Which MFS platforms do you use?", "text_bn": "কোন এমএফএস প্ল্যাটফর্ম ব্যবহার করেন?", "options": ["bKash", "Nagad", "Rocket", "Upay", "SureCash", "None"], "required": True},
            {"id": "B2", "type": "radio", "text_en": "How often do you use MFS?", "text_bn": "কত ঘন ঘন ব্যবহার করেন?", "options": ["Multiple times/day", "Once/day", "Few times/week", "Once/week", "Rarely"], "required": True},
            {"id": "B3", "type": "radio", "text_en": "Typical transaction size?", "text_bn": "সাধারণ লেনদেনের পরিমাণ?", "options": ["<500 BDT", "500-2k", "2-5k", "5-10k", ">10k"], "required": True},
            {"id": "B4", "type": "checkbox", "text_en": "Primary use cases?", "text_bn": "প্রধান ব্যবহার?", "options": ["Send money", "Receive money", "Recharge", "Bill payment", "Shopping", "Merchant pay", "Cash out"], "required": True},
        ]
    },
    {
        "section_id": "C",
        "title_en": "Section C: Scam Exposure",
        "title_bn": "অনুচ্ছেদ গ: প্রতারণার অভিজ্ঞতা",
        "questions": [
            {"id": "C1", "type": "radio", "text_en": "Received suspicious MFS message in last 6 months?", "text_bn": "গত ৬ মাসে সন্দেহজনক বার্তা পেয়েছেন?", "options": ["Yes, many times", "Yes, once/twice", "No", "Not sure"], "required": True},
            {"id": "C2", "type": "checkbox", "text_en": "Through which channels?", "text_bn": "কোন মাধ্যমে?", "options": ["SMS", "WhatsApp", "Facebook", "Phone call", "Email", "Other"], "required": False},
            {"id": "C3", "type": "radio", "text_en": "Did you respond?", "text_bn": "জবাব দিয়েছিলেন?", "options": ["Yes", "No", "Prefer not to say"], "required": True},
            {"id": "C4", "type": "radio", "text_en": "Financially harmed?", "text_bn": "আর্থিক ক্ষতি?", "options": ["Yes, significant (>1000 BDT)", "Yes, small (<1000 BDT)", "No, realized in time", "Never responded", "Prefer not to say"], "required": True},
            {"id": "C5", "type": "radio", "text_en": "Reported to authority?", "text_bn": "কর্তৃপক্ষকে জানিয়েছিলেন?", "options": ["Yes, MFS provider", "Yes, police", "Yes, Bangladesh Bank", "No, didn't know where", "No, didn't think it would help"], "required": True},
        ]
    },
    {
        "section_id": "D",
        "title_en": "Section D: Digital Literacy (1=Strongly Disagree, 5=Strongly Agree)",
        "title_bn": "অনুচ্ছেদ ঘ: ডিজিটাল সাক্ষরতা",
        "questions": [
            {"id": "D1", "type": "likert", "text_en": "I know how to verify official bKash/Nagad messages", "text_bn": "আমি জানি কীভাবে অফিশিয়াল বার্তা যাচাই করতে হয়", "scale": [1,2,3,4,5], "required": True},
            {"id": "D2", "type": "likert", "text_en": "I can identify suspicious links", "text_bn": "সন্দেহজনক লিঙ্ক চিনতে পারি", "scale": [1,2,3,4,5], "required": True},
            {"id": "D3", "type": "likert", "text_en": "I understand OTP/PIN should not be shared", "text_bn": "OTP/PIN শেয়ার করা উচিত নয় বুঝি", "scale": [1,2,3,4,5], "required": True},
            {"id": "D4", "type": "likert", "text_en": "I know how to check if a website is secure", "text_bn": "ওয়েবসাইট নিরাপদ কিনা জানি", "scale": [1,2,3,4,5], "required": True},
            {"id": "D5", "type": "likert", "text_en": "I am comfortable with mobile financial transactions", "text_bn": "মোবাইল লেনদেনে স্বাচ্ছন্দ্যবোধ করি", "scale": [1,2,3,4,5], "required": True},
        ]
    },
    {
        "section_id": "F",
        "title_en": "Section F: Message Classification Task",
        "title_bn": "অনুচ্ছেদ চ: বার্তা শ্রেণীবিভাগ",
        "description": "Classify each message as Legitimate or Scam",
        "questions": [
            {"id": "F1", "type": "radio", "text_en": "Msg1: 'Dear bKash user, your account suspended. Verify: bkash-verify.tk/login. Enter OTP.'", "is_scam": True, "options": ["Legitimate", "Scam", "Not sure"], "required": True},
            {"id": "F2", "type": "radio", "text_en": "Msg2: 'Your bKash cash-in 500 BDT successful. TxID:8XJ2MN. Balance:2,450 BDT.'", "is_scam": False, "options": ["Legitimate", "Scam", "Not sure"], "required": True},
            {"id": "F3", "type": "radio", "text_en": "Msg3: 'Congratulations! Won 10,000 BDT bKash bonus. Claim: short.link/xyz123. Limited time!'", "is_scam": True, "options": ["Legitimate", "Scam", "Not sure"], "required": True},
            {"id": "F4", "type": "radio", "text_en": "Msg4: 'Nagad: Your verification code is 784321. Do not share this code.'", "is_scam": False, "options": ["Legitimate", "Scam", "Not sure"], "required": True},
            {"id": "F5", "type": "radio", "text_en": "Msg5: 'DBBL Rocket under maintenance. Update info: rocket-update.xyz/form'", "is_scam": True, "options": ["Legitimate", "Scam", "Not sure"], "required": True},
        ]
    }
]


def generate_html_form(output_path):
    """Generate HTML survey form."""
    css = """
    * { box-sizing: border-box; }
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5; }
    .header { background: linear-gradient(135deg, #e31e24, #ff6b6b); color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }
    .header h1 { margin: 0 0 10px 0; font-size: 24px; }
    .consent { background: #fff3cd; border: 1px solid #ffc107; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
    .section { background: white; padding: 25px; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
    .section-title { color: #e31e24; font-size: 18px; font-weight: bold; margin-bottom: 5px; }
    .bn { color: #006847; font-size: 14px; display: block; margin-top: 3px; }
    .question { margin-bottom: 20px; padding-bottom: 15px; border-bottom: 1px solid #eee; }
    .question-text { font-weight: 600; margin-bottom: 10px; }
    .option { margin-bottom: 8px; }
    .option label { cursor: pointer; padding: 5px 10px; display: block; border-radius: 5px; }
    .option label:hover { background: #f0f0f0; }
    input[type="radio"], input[type="checkbox"] { margin-right: 10px; transform: scale(1.2); }
    .likert { display: flex; justify-content: space-between; gap: 5px; margin-top: 10px; }
    .likert-opt { text-align: center; flex: 1; }
    .likert-opt input { display: block; margin: 0 auto 5px; }
    .likert-opt label { font-size: 12px; }
    .required { color: #e31e24; }
    .submit-btn { background: linear-gradient(135deg, #e31e24, #ff6b6b); color: white; padding: 15px 40px; border: none; border-radius: 25px; font-size: 16px; cursor: pointer; display: block; margin: 30px auto; }
    .submit-btn:hover { opacity: 0.9; }
    """
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>MFS Scam Susceptibility Survey</title>
<style>{css}</style></head>
<body>
<div class="header"><h1>MFS Scam Susceptibility Survey</h1>
<p>Measuring Mobile Financial Services Fraud Exposure in Bangladesh</p>
<p style="font-size:12px;margin-top:10px;">East-West University Bangladesh | Research Ethics Approved</p></div>
<div class="consent"><strong>Informed Consent</strong>
<p>You are invited to participate in a research study about MFS fraud. Your responses are anonymous. 
Participation is voluntary and you may withdraw at any time.</p>
<label><input type="checkbox" required> I consent to participate</label></div>
<form id="surveyForm" action="#" method="POST">
"""
    
    for section in SURVEY_SECTIONS:
        html += f'<div class="section"><div class="section-title">{section["title_en"]}</div>'
        if "title_bn" in section:
            html += f'<div class="section-title bn">{section["title_bn"]}</div>'
        if "description" in section:
            html += f'<p>{section["description"]}</p>'
        
        for q in section["questions"]:
            req = ' <span class="required">*</span>' if q.get("required") else ""
            html += f'<div class="question"><div class="question-text">{q["id"]}. {q["text_en"]}{req}'
            if "text_bn" in q:
                html += f'<span class="bn">{q["text_bn"]}</span>'
            html += '</div><div class="options">'
            
            if q["type"] == "likert":
                html += '<div class="likert">'
                labels = ["Strongly Disagree", "Disagree", "Neutral", "Agree", "Strongly Agree"]
                for i, val in enumerate(q["scale"]):
                    lbl = labels[i] if i < len(labels) else str(val)
                    html += f'<div class="likert-opt"><input type="radio" name="{q["id"]}" value="{val}" id="{q["id"]}_{val}" required><label for="{q["id"]}_{val}">{val}<br>{lbl}</label></div>'
                html += '</div>'
            else:
                itype = "checkbox" if q["type"] == "checkbox" else "radio"
                for opt in q["options"]:
                    oid = f"{q['id']}_{opt[:20].replace(' ', '_')}"
                    req_attr = " required" if q.get("required") and itype == "radio" else ""
                    html += f'<div class="option"><label><input type="{itype}" name="{q["id"]}" value="{opt}" id="{oid}"{req_attr}> {opt}</label></div>'
            
            html += '</div></div>'
        html += '</div>'
    
    html += '<button type="submit" class="submit-btn">Submit Survey</button></form></body></html>'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"[+] HTML survey form: {output_path}")
    return output_path


def generate_json_schema(output_path):
    """Generate JSON schema for survey platforms."""
    schema = {
        "survey_title": "MFS Scam Susceptibility Survey",
        "version": "1.0",
        "institution": "East-West University Bangladesh",
        "language": ["en", "bn"],
        "estimated_duration_minutes": 12,
        "sections": SURVEY_SECTIONS,
        "scoring": {
            "digital_literacy_score": {"items": ["D1","D2","D3","D4","D5"], "range": [1,5]},
            "susceptibility_score": {
                "items": ["F1","F2","F3","F4","F5"],
                "correct_answers": {"F1":"Scam","F2":"Legitimate","F3":"Scam","F4":"Legitimate","F5":"Scam"}
            }
        }
    }
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)
    print(f"[+] JSON schema: {output_path}")


class SurveyDataProcessor:
    def __init__(self, csv_path):
        self.df = pd.read_csv(csv_path)
        self.clean_df = None
        self.scores = {}
    
    def clean_data(self):
        df = self.df.copy()
        df['completion_rate'] = df.notna().sum(axis=1) / len(df.columns)
        df = df[df['completion_rate'] >= 0.5]
        if 'duration' in df.columns:
            df = df[df['duration'] >= 180]
        if 'ip_address' in df.columns:
            df = df.drop_duplicates(subset=['ip_address'], keep='first')
        self.clean_df = df
        print(f"Original: {len(self.df)}, After cleaning: {len(df)}, Removed: {len(self.df)-len(df)}")
        return df
    
    def compute_scores(self):
        if self.clean_df is None: self.clean_data()
        df = self.clean_df
        lit_cols = [c for c in ['D1','D2','D3','D4','D5'] if c in df.columns]
        if lit_cols:
            df['digital_literacy_score'] = df[lit_cols].mean(axis=1)
            self.scores['digital_literacy'] = df['digital_literacy_score'].describe().to_dict()
        ca = {"F1":"Scam","F2":"Legitimate","F3":"Scam","F4":"Legitimate","F5":"Scam"}
        vig_cols = [c for c in ['F1','F2','F3','F4','F5'] if c in df.columns]
        if vig_cols:
            correct = sum((df[c] == ca[c]).astype(int) for c in vig_cols if c in ca)
            df['susceptibility_score'] = 100 - (correct / len(vig_cols) * 100)
            self.scores['susceptibility'] = df['susceptibility_score'].describe().to_dict()
        self.clean_df = df
        return self.scores
    
    def generate_report(self, output_path):
        if not self.scores: self.compute_scores()
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_responses': len(self.df),
            'valid_responses': len(self.clean_df),
            'scores': self.scores,
        }
        with open(output_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"[+] Report saved: {output_path}")
        return report


def main():
    parser = argparse.ArgumentParser(description="Survey Form Generator & Data Processor")
    parser.add_argument("--generate", action="store_true", help="Generate survey form")
    parser.add_argument("--output", default="./survey", help="Output directory")
    parser.add_argument("--process", help="Process responses CSV")
    parser.add_argument("--report", help="Generate analysis report")
    args = parser.parse_args()
    
    os.makedirs(args.output, exist_ok=True)
    
    if args.generate:
        generate_html_form(os.path.join(args.output, "survey_form.html"))
        generate_json_schema(os.path.join(args.output, "survey_schema.json"))
        print(f"[*] Survey generated in: {args.output}/")
    
    if args.process:
        processor = SurveyDataProcessor(args.process)
        processor.clean_data()
        processor.compute_scores()
        if args.report: processor.generate_report(args.report)
        print("[*] Data processing complete!")

if __name__ == "__main__":
    main()
