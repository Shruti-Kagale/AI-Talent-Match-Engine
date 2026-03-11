import os
from pdf2image import convert_from_path
import pytesseract

# Paths
pdf_folder = r"C:\Users\shrut\OneDrive\Desktop\New folder\Resumes"   # Folder containing PDFs
output_folder = r"C:\Users\shrut\OneDrive\Desktop\New folder\artifacts"  # Save extracted text here

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Process each PDF in the folder
for file_name in os.listdir(pdf_folder):
    if file_name.lower().endswith(".pdf"):
        pdf_path = os.path.join(pdf_folder, file_name)
        print(f"Processing: {file_name}")

        try:
            # Convert PDF to images (one image per page)
            images = convert_from_path(pdf_path)

            # Extract text from all pages
            full_text = ""
            for img in images:
                text = pytesseract.image_to_string(img)
                full_text += text + "\n\n"

            # Save text to a .txt file in artifacts
            txt_file_name = os.path.splitext(file_name)[0] + ".txt"
            txt_path = os.path.join(output_folder, txt_file_name)
            with open(txt_path, "w", encoding="utf-8") as f:
                f.write(full_text)

            print(f"Saved: {txt_file_name} in artifacts")

        except Exception as e:
            print(f"Error processing {file_name}: {e}")

print("All PDFs processed! Text files are saved in the 'artifacts' folder.")
