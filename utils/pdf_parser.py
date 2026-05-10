from pathlib import Path
from typing import BinaryIO

from pypdf import PdfReader


def save_uploaded_pdf(uploaded_file: BinaryIO, upload_dir: str = "uploads") -> str:
    Path(upload_dir).mkdir(parents=True, exist_ok=True)
    file_path = Path(upload_dir) / uploaded_file.name
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(file_path)


def extract_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            pages.append(page_text)
    return "\n".join(pages)