"""
Reads:
  - artifacts/resumes_clean.csv or .xlsx  (must contain: resume_name, cleaned_text)
  - artifacts/jobs_clean.csv or .xlsx     (must contain: job_id, jd_text)

Outputs:
  - artifacts/resume_skills.xlsx
  - artifacts/jd_skills.xlsx
"""

import pandas as pd
from pathlib import Path

# -------------------------
# Paths
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKILLS_CSV = Path(__file__).resolve().parent / "skills_list.csv"

RESUMES_X = PROJECT_ROOT / "artifacts" / "resumes_clean"
JDS_X = PROJECT_ROOT / "artifacts" / "jobs_clean"

OUT_RESUME = PROJECT_ROOT / "artifacts" / "resume_skills.xlsx"
OUT_JD = PROJECT_ROOT / "artifacts" / "jd_skills.xlsx"


# -------------------------
# Load skills list
# -------------------------
def load_skills():
    if not SKILLS_CSV.exists():
        raise FileNotFoundError(f"Missing skills_list.csv at {SKILLS_CSV}")

    df = pd.read_csv(SKILLS_CSV, header=None)
    skills = [str(s).strip() for s in df[0].tolist() if str(s).strip()]

    # Lowercase for matching
    skills = [s.lower() for s in skills]

    return skills


# -------------------------
# Detect text column
# -------------------------
def get_text_column(df):
    for candidate in ("cleaned_text", "clean_text", "jd_text", "text", "resume_text", "description"):
        if candidate in df.columns:
            return candidate
    return df.columns[-1]


# -------------------------
# Extract skills (SIMPLE SUBSTRING MATCH)
# -------------------------
def extract_skills_from_text(text, skills):
    if not isinstance(text, str):
        return ""

    txt = text.lower()
    found = set()

    for skill in skills:
        if skill in txt:           # <-- Quick Fix applied
            found.add(skill)

    return ";".join(sorted(found))


# -------------------------
# Read CSV or Excel safely
# -------------------------
def read_file_auto(path_base):
    for ext in [".csv", ".xlsx"]:
        path = path_base.with_suffix(ext)
        if path.exists():
            if ext == ".csv":
                return pd.read_csv(path)
            else:
                return pd.read_excel(path)
    raise FileNotFoundError(f"Missing: {path_base}.csv or {path_base}.xlsx")


# -------------------------
# Main process
# -------------------------
def process():
    skills = load_skills()

    resumes = read_file_auto(RESUMES_X)
    jobs = read_file_auto(JDS_X)

    r_text_col = get_text_column(resumes)
    j_text_col = get_text_column(jobs)

    # Ensure ID columns
    if "resume_name" not in resumes.columns:
        resumes = resumes.rename(columns={resumes.columns[0]: "resume_name"})
    if "job_id" not in jobs.columns:
        jobs = jobs.rename(columns={jobs.columns[0]: "job_id"})

    # Extract skills
    resumes["skills"] = resumes[r_text_col].apply(lambda t: extract_skills_from_text(t, skills))
    jobs["skills"] = jobs[j_text_col].apply(lambda t: extract_skills_from_text(t, skills))

    # Save
    resumes.to_excel(OUT_RESUME, index=False)
    jobs.to_excel(OUT_JD, index=False)

    print(f"[OK] Resume skills saved -> {OUT_RESUME}")
    print(f"[OK] JD skills saved -> {OUT_JD}")


if __name__ == "__main__":
    process()
