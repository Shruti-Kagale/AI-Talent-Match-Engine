import os
import pdfplumber
import pandas as pd

# Folder where JD PDFs are stored
jd_dir = "C:/Users/shrut/OneDrive/Desktop/New folder/JD";

jobs = []

# Loop through each JD PDF
for file in os.listdir(jd_dir):
    if file.endswith(".pdf"):
        with pdfplumber.open(os.path.join(jd_dir, file)) as pdf:
            text = ""
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
            jobs.append({
                "job_title": file.replace(".pdf", ""),
                "jd_text": text.strip()
            })

# Save extracted jobs to artifacts
os.makedirs("artifacts", exist_ok=True)
jobs_df = pd.DataFrame(jobs)
jobs_df.to_excel("artifacts/jobs_clean.xlsx", index=False)

print(" Job descriptions extracted and saved to artifacts/jobs_clean.xlsx")
