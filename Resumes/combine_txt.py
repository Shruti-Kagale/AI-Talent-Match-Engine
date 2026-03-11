import os
import pandas as pd

TXT_FOLDER = r"C:\Users\shrut\OneDrive\Desktop\New folder\artifacts"
OUTPUT_CSV = os.path.join(TXT_FOLDER, "resumes_raw.csv")

def combine_txt_to_csv(txt_dir, output_csv):
    txt_files = [f for f in os.listdir(txt_dir) if f.lower().endswith(".txt")]

    data = []
    for file in txt_files:
        path = os.path.join(txt_dir, file)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        data.append({"filename": file, "text": text})

    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"✔ CSV generated: {output_csv}")

combine_txt_to_csv(TXT_FOLDER, OUTPUT_CSV)
