"""
Handles turning an uploaded file into plain text so the LLM can read it.
Kept intentionally simple (no OCR) per the assignment note: "Production-grade
OCR or document parsing is not required."
"""
from pathlib import Path
from pypdf import PdfReader


def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)
    text_parts = []
    for page in reader.pages:
        text_parts.append(page.extract_text() or "")
    return "\n".join(text_parts).strip()


def extract_text_from_upload(file_path: str, filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    if suffix in (".txt", ".eml"):
        return Path(file_path).read_text(errors="ignore")
    # Fallback: try reading as plain text
    try:
        return Path(file_path).read_text(errors="ignore")
    except Exception:
        return ""
