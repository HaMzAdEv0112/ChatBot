import re
from pathlib import Path

from pypdf import PdfReader

from app.config import settings


def chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> list[str]:
    chunk_size = chunk_size or settings.chunk_size
    overlap = overlap or settings.chunk_overlap
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return []

    chunks: list[str] = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = [page.extract_text() or "" for page in reader.pages]
    return "\n".join(pages)


def extract_text_from_file(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    if suffix in {".txt", ".md"}:
        return file_path.read_text(encoding="utf-8", errors="ignore")
    raise ValueError(f"Unsupported file type: {suffix}")


def ingest_file(file_path: Path) -> list[dict]:
    text = extract_text_from_file(file_path)
    chunks = chunk_text(text)
    return [
        {
            "text": chunk,
            "metadata": {
                "source": file_path.name,
                "chunk_index": i,
            },
        }
        for i, chunk in enumerate(chunks)
    ]
