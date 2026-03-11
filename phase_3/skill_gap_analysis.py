"""
Skill Gap Analysis per Resume (CSV or XLSX)

Generates:
- skill_gaps_per_resume.xlsx → matched & missing skills, skill_ratio
"""

import pandas as pd
from pathlib import Path

# ----------------------------
# PATH SETUP
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # "New folder"
ARTIFACTS = PROJECT_ROOT / "artifacts"

# You can switch between CSV or XLSX here
RESUME_SKILLS_FILE = ARTIFACTS / "resume_skills.xlsx"  # or "resumes_clean.csv"
JD_SKILLS_FILE = ARTIFACTS / "jd_skills.xlsx"          # or "jobs_clean.csv"
OUT_SKILL_GAP = ARTIFACTS / "skill_gaps_per_resume.xlsx"

# ----------------------------
# HELPER: load CSV or Excel
# ----------------------------
def load_file(path):
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix.lower() == ".csv":
        return pd.read_csv(path)
    elif path.suffix.lower() in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {path}")

# ----------------------------
# LOAD DATA
# ----------------------------
resume_skills_df = load_file(RESUME_SKILLS_FILE)
jd_skills_df = load_file(JD_SKILLS_FILE)

# ----------------------------
# ENSURE ESSENTIAL COLUMNS
# ----------------------------
for df, name in [(resume_skills_df, "resume_skills"), (jd_skills_df, "jd_skills")]:
    if "skills" not in df.columns:
        raise ValueError(f"{name} file must have a 'skills' column")
if "resume_name" not in resume_skills_df.columns:
    resume_skills_df = resume_skills_df.rename(columns={resume_skills_df.columns[0]: "resume_name"})
if "job_id" not in jd_skills_df.columns:
    jd_skills_df = jd_skills_df.rename(columns={jd_skills_df.columns[0]: "job_id"})

# Convert skills column to list of lowercase skills
resume_skills_df["skills"] = resume_skills_df["skills"].astype(str).str.split(",").apply(lambda x: [s.strip().lower() for s in x])
jd_skills_df["skills"] = jd_skills_df["skills"].astype(str).str.split(",").apply(lambda x: [s.strip().lower() for s in x])

# ----------------------------
# COMPUTE SKILL GAPS PER RESUME
# ----------------------------
def parse_skills(text):
    # Handle both comma and semicolon separators
    return set(s.strip().lower() for s in str(text).replace(';',',').split(',') if s.strip())

results = []

for _, jd in jd_skills_df.iterrows():
    job_id = jd["job_id"]
    jd_skills = parse_skills(jd["skills"])

    for _, resume in resume_skills_df.iterrows():
        resume_name = resume["resume_name"]
        resume_skills = parse_skills(resume["skills"])

        matched_skills = jd_skills & resume_skills
        missing_skills = jd_skills - resume_skills

        num_matched = len(matched_skills)
        num_missing = len(missing_skills)
        skill_ratio = num_matched / (num_matched + num_missing) if (num_matched + num_missing) > 0 else 0

        results.append({
            "job_id": job_id,
            "resume_name": resume_name,
            "matched_skills": ", ".join(sorted(matched_skills)),
            "missing_skills": ", ".join(sorted(missing_skills)),
            "num_matched": num_matched,
            "num_missing": num_missing,
            "skill_ratio": skill_ratio
        })

# ----------------------------
# SAVE OUTPUT
# ----------------------------
gap_df = pd.DataFrame(results)
gap_df.to_excel(OUT_SKILL_GAP, index=False)
print(f"[OK] Resume-level skill gaps saved → {OUT_SKILL_GAP}")
