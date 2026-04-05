from dotenv import load_dotenv
load_dotenv()

import fitz
import re
import os

def extract_text_from_pdf(pdf_path: str) -> str:
    doc = fitz.open(pdf_path)
    full_text = ""
    for page in doc:
        full_text += page.get_text()
    doc.close()
    return full_text.strip()

def extract_text_from_docx(docx_path: str) -> str:
    from docx import Document
    doc = Document(docx_path)
    full_text = ""
    for paragraph in doc.paragraphs:
        full_text += paragraph.text + "\n"
    return full_text.strip()

def clean_resume_text(text: str) -> str:
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()

def parse_resume(file_path: str) -> str:
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        raw_text = extract_text_from_pdf(file_path)
    elif ext in [".docx", ".doc"]:
        raw_text = extract_text_from_docx(file_path)
    else:
        return "Unsupported file format. Please upload PDF or Word document."
    
    cleaned = clean_resume_text(raw_text)
    return cleaned

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = parse_resume(sys.argv[1])
        print(f"Extracted {len(result)} characters")
        print(result[:500])
    else:
        print("Usage: python resume_parser.py yourresume.pdf")