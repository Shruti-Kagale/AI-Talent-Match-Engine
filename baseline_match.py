# baseline_match.py

import os
import pandas as pd
from sentence_transformers import SentenceTransformer, util

# Paths
RESUMES_FILE = "artifacts/resumes_clean.xlsx"
JDS_FILE = "artifacts/jobs_clean.xlsx"
OUTPUT_FILE = "artifacts/baseline_results_sbert.xlsx"

# ---- Step 1: Load Data ----
resumes_df = pd.read_excel(RESUMES_FILE)
jobs_df = pd.read_excel(JDS_FILE)

# Columns: adjust if different in your files
resume_texts = resumes_df["clean_text"].tolist()
resume_names = resumes_df["resume_id"].tolist()
jd_texts = jobs_df["clean_text"].tolist()
jd_names = jobs_df["job_id"].tolist()

# ---- Step 2: Define Skill Normalization Dictionary ----
skill_map = {
    "ml": "machine learning",
    "machine learning": "machine learning",
    "nlp": "natural language processing",
    "natural language processing": "natural language processing",
    "ai": "artificial intelligence",
    "artificial intelligence": "artificial intelligence",
    "sql": "structured query language",
    "python": "python",   # keep as is
    "java": "java"        # example, you can expand later
}

def normalize_text(text):
    """Replace skills/keywords with normalized forms"""
    text_lower = text.lower()
    for k, v in skill_map.items():
        if k in text_lower:
            text_lower = text_lower.replace(k, v)
    return text_lower

resume_texts = [normalize_text(t) for t in resume_texts]
jd_texts = [normalize_text(t) for t in jd_texts]

# ---- Step 3: Encode with SBERT ----
model = SentenceTransformer("all-MiniLM-L6-v2")
resume_embeddings = model.encode(resume_texts, convert_to_tensor=True)
jd_embeddings = model.encode(jd_texts, convert_to_tensor=True)

# ---- Step 4: Compute Similarity ----
results = []
for i, jd in enumerate(jd_names):
    sims = util.cos_sim(jd_embeddings[i], resume_embeddings)[0].cpu().tolist()
    for r, score in zip(resume_names, sims):
        results.append({
            "Job_Description": jd,
            "Resume": r,
            "Match_Score": round(score * 100, 2)
        })

# ---- Step 5: Save Results ----
df = pd.DataFrame(results)

# Save full results
df.to_excel(OUTPUT_FILE, index=False)

# Also save Top-5 per JD
top5 = df.sort_values(["Job_Description", "Match_Score"],
                      ascending=[True, False]).groupby("Job_Description").head(5)
top5.to_excel("artifacts/top5_results_sbert.xlsx", index=False)

print("✅ Matching complete!")
print(f"All results: {OUTPUT_FILE}")
print("Top-5 per JD: artifacts/top5_results_sbert.xlsx")
