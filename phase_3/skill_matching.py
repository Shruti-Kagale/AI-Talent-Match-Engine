"""
Skill Gap Analysis per Resume (Updated)

Generates:
- skill_gaps_per_resume.xlsx → matched & missing skills, skill_ratio
"""

import pandas as pd
from pathlib import Path

# ----------------------------
# PATH SETUP
# ----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]  # adjust if needed
ARTIFACTS = PROJECT_ROOT / "artifacts"

RESUMES_X = ARTIFACTS / "resumes_clean.csv"   # resumes CSV
JDS_X = ARTIFACTS / "jobs_clean.xlsx"        # job descriptions XLSX
OUT_SKILL_GAP = ARTIFACTS / "skill_gaps_per_resume.xlsx"

# ----------------------------
# CHECK FILES EXIST
# ----------------------------
for path in [RESUMES_X, JDS_X]:
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

# ----------------------------
# LOAD DATA
# ----------------------------
resumes = pd.read_csv(RESUMES_X)
jobs = pd.read_excel(JDS_X)

# ----------------------------
# SKILL LIST
# ----------------------------
skill_list = [
    "python","java","c","c++","machine learning","deep learning","nlp",
    "natural language processing","sql","mysql","postgresql","mongodb",
    "pandas","numpy","scikit-learn","sklearn","tensorflow","pytorch","keras",
    "docker","kubernetes","aws","azure","gcp","spark","hadoop","etl",
    "airflow","rest api","api","django","flask","react","javascript","html",
    "css","git","linux","data analysis","data visualization","tableau","power bi",
    "excel","statistics","regression","classification","clustering","text mining",
    "computer vision","image processing","feature engineering","modeling","a/b testing",
    "ci/cd","bash","shell","security","networking","devops","mlops",
    "customer service","guest relations","pos operation","dining room setup",
    "restaurant intercom operation","upselling","wine pairing","complaint resolution",
    "staff training","table management","seating coordination","hospitality operations",
    "customer relationships","office administration","scheduling","calendar management",
    "shipping logistics","communication logistics","crm data entry","data entry",
    "typing","10-key typing","ms office","ms word","ms excel","report preparation",
    "email handling","clerical accuracy","organization","documentation",
    "trademark prosecution","intellectual property law","legal research",
    "legal writing","licensing agreements","portfolio management","contract management",
    "dispute resolution","negotiation","communication","communication skills",
    "problem solving","decision making","attention to detail","teamwork","multitasking",
    "dependability","stress tolerance","strategic thinking","leadership",
    "team leadership","efficiency improvement","diligent research"
]

# ----------------------------
# HELPER: auto-detect text column
# ----------------------------
def get_text_column(df):
    candidates = ["cleaned_text", "text", "resume_text", "description"]
    for c in candidates:
        if c in df.columns:
            return c
    return df.columns[-1]  # fallback to last column

r_col = get_text_column(resumes)
j_col = get_text_column(jobs)

# Ensure essential columns exist
if "resume_name" not in resumes.columns:
    resumes = resumes.rename(columns={resumes.columns[0]: "resume_name"})
if "job_id" not in jobs.columns:
    jobs = jobs.rename(columns={jobs.columns[0]: "job_id"})

# ----------------------------
# SKILL EXTRACTION FUNCTION
# ----------------------------
def extract_skills(text):
    text_lower = str(text).lower()
    return {skill for skill in skill_list if skill in text_lower}

# ----------------------------
# COMPUTE SKILL GAPS PER RESUME
# ----------------------------
results = []

for _, job in jobs.iterrows():
    job_id = job["job_id"]
    jd_text = str(job[j_col])
    jd_skills = extract_skills(jd_text)

    for _, resume in resumes.iterrows():
        resume_name = resume["resume_name"]
        resume_file = ARTIFACTS / resume_name  # resume text files are in artifacts

        # Read actual resume text
        if not resume_file.exists():
            print(f"[WARN] Resume file not found: {resume_file}")
            resume_text = ""
        else:
            with open(resume_file, 'r', encoding='utf-8') as f:
                resume_text = f.read()

        resume_skills = extract_skills(resume_text)

        matched_skills = sorted(resume_skills & jd_skills)
        missing_skills = sorted(jd_skills - resume_skills)

        num_matched = len(matched_skills)
        num_missing = len(missing_skills)
        skill_ratio = num_matched / (num_matched + num_missing) if (num_matched + num_missing) > 0 else 0

        results.append({
            "job_id": job_id,
            "resume_name": resume_name,
            "matched_skills": ", ".join(matched_skills),
            "missing_skills": ", ".join(missing_skills),
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
