import re
import pandas as pd
import numpy as np
from pathlib import Path

# -----------------------------------
# ABSOLUTE PATHS
# -----------------------------------
IN_CSV = r"C:\Users\shrut\OneDrive\Desktop\New folder\artifacts\resumes_raw.csv"
OUT_CSV = r"C:\Users\shrut\OneDrive\Desktop\New folder\artifacts\resumes_clean.csv"

STOPWORDS = {
    "a","an","the","and","or","but","if","in","on","with","of","for","to","from",
    "is","am","are","was","were","be","been","being","at","by","this","that",
    "it","as","so","such","not","no","too","very"
}

BASIC_SKILLS = [
    "python","java","sql","c++","excel","tableau",
    "machine learning","deep learning","nlp","pandas","numpy",
]

def clean_text(text: str) -> str:
    if pd.isna(text):
        return ""
    text = text.lower()
    text = re.sub(r"\S+@\S+", " ", text)
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)
    text = re.sub(r"\+?\d[\d\s().-]{7,}\d", " ", text)
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    tokens = [w for w in text.split() if w not in STOPWORDS]
    return " ".join(tokens)

def extract_years_experience(text: str) -> float:
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*(?:years?|yrs)", text)
    return float(matches[0]) if matches else 0.0

def extract_skills(text: str):
    found = []
    for skill in BASIC_SKILLS:
        if skill in text:
            found.append(skill)
    return ";".join(found)

def main():
    print("📥 Reading:", IN_CSV)
    df = pd.read_csv(IN_CSV)

    # REQUIRED columns
    if "text" not in df.columns:
        raise Exception("ERROR: CSV must contain a column named 'text'.")

    cleaned_rows = []
    for _, row in df.iterrows():
        raw = str(row["text"])
        cleaned = clean_text(raw)
        years = extract_years_experience(cleaned)
        skills = extract_skills(cleaned)

        cleaned_rows.append({
            "filename": row.get("filename", ""),
            "clean_text": cleaned,
            "years_experience": years,
            "skills_found": skills,
            "raw_length": len(raw)
        })

    out_df = pd.DataFrame(cleaned_rows)
    out_df.to_csv(OUT_CSV, index=False, encoding="utf-8")

    print("✅ Cleaning complete!")
    print("📄 Saved:", OUT_CSV)

if __name__ == "__main__":
    main()
