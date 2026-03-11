import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ----------------------------
# PATH SETUP
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS = PROJECT_ROOT / "artifacts"

RESUMES_X = ARTIFACTS / "resume_skills.xlsx"
JDS_X = ARTIFACTS / "jd_skills.xlsx"
SKILL_GAP_FILE = ARTIFACTS / "skill_gaps_per_resume.xlsx"
OUT_BASELINE = ARTIFACTS / "baseline_results.csv"
OUT_ALL = ARTIFACTS / "all_resumes_ranked.xlsx"

W_SIM = 0.7
W_SKILL = 0.3

# ----------------------------
# Helpers
# ----------------------------
def get_text_column(df):
    for c in ["cleaned_text", "text", "resume_text", "description"]:
        if c in df.columns:
            return c
    return df.columns[-1]

def read_skill_gap(file_path):
    if file_path.suffix.lower() == ".xlsx":
        return pd.read_excel(file_path)
    return pd.read_csv(file_path)

def parse_skills(x):
    if pd.isna(x):
        return []
    if isinstance(x, list):
        return [s.strip().lower() for s in x if s.strip() and s.strip().lower() != 'c']
    if isinstance(x, str):
        x = x.replace("[","").replace("]","").replace("'","").replace('"','')
        return [s.strip().lower() for s in x.split(",") if s.strip() and s.strip().lower() != 'c']
    return []

# ----------------------------
# Compute baseline similarity
# ----------------------------
def compute_baseline_similarity():
    resumes = pd.read_excel(RESUMES_X)
    jobs = pd.read_excel(JDS_X)

    r_col = get_text_column(resumes)
    j_col = get_text_column(jobs)

    if "resume_name" not in resumes.columns:
        resumes = resumes.rename(columns={resumes.columns[0]: "resume_name"})
    if "job_id" not in jobs.columns:
        jobs = jobs.rename(columns={jobs.columns[0]: "job_id"})

    resumes[r_col] = resumes[r_col].astype(str).fillna("").str.strip()
    jobs[j_col] = jobs[j_col].astype(str).fillna("").str.strip()

    results = []
    for _, job in jobs.iterrows():
        job_id = job["job_id"]
        jd_text = str(job[j_col]).strip()
        if jd_text == "":
            continue
        valid_resumes = resumes[resumes[r_col] != ""]
        docs = [jd_text] + valid_resumes[r_col].tolist()
        try:
            tfidf = TfidfVectorizer(token_pattern=r"(?u)\b\w+\b").fit_transform(docs)
            sim_scores = cosine_similarity(tfidf[0:1], tfidf[1:]).flatten()
        except:
            sim_scores = [0] * len(valid_resumes)
        for rname, score in zip(valid_resumes["resume_name"], sim_scores):
            results.append({"job_id": job_id, "resume_name": rname, "similarity_score": float(score)})

    baseline_df = pd.DataFrame(results)
    baseline_df.to_csv(OUT_BASELINE, index=False)
    return baseline_df

# ----------------------------
# Rank all resumes
# ----------------------------
def rank_all_resumes():
    baseline = pd.read_csv(OUT_BASELINE)
    gap = read_skill_gap(SKILL_GAP_FILE)
    for col in ["matched_skills","missing_skills"]:
        if col in gap.columns:
            gap[col] = gap[col].apply(parse_skills)

    gap["num_matched"] = gap["matched_skills"].apply(len)
    gap["num_missing"] = gap["missing_skills"].apply(len)
    gap["skill_ratio"] = gap.apply(lambda r: r["num_matched"]/(r["num_matched"]+r["num_missing"]) if (r["num_matched"]+r["num_missing"])>0 else 0, axis=1)

    merged = pd.merge(baseline, gap, on=["job_id","resume_name"], how="inner")
    merged["final_score"] = W_SIM*merged["similarity_score"] + W_SKILL*merged["skill_ratio"]

    merged["matched_skills"] = merged["matched_skills"].apply(lambda x: ", ".join(sorted(x)))
    merged["missing_skills"] = merged["missing_skills"].apply(lambda x: ", ".join(sorted(x)))

    merged["rank"] = merged.groupby("job_id")["final_score"].rank(ascending=False, method="first").astype(int)
    merged.to_excel(OUT_ALL, index=False)
    print(f"[OK] All resumes ranked → {OUT_ALL}")

# ----------------------------
# RUN
# ----------------------------
if __name__ == "__main__":
    compute_baseline_similarity()
    rank_all_resumes()
