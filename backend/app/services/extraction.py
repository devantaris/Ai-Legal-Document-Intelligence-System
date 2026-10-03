"""Text extraction from uploaded files, preserving page boundaries.

PDFs are split into real pages. DOCX/TXT have no intrinsic pages, so text is
split into ~3.5k-character "virtual pages" at paragraph boundaries — this
keeps page-level citations meaningful for every format.
"""

from pathlib import Path

import pymupdf
from docx import Document as DocxDocument

VIRTUAL_PAGE_CHARS = 3500

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".txt", ".md"}


class UnsupportedFileError(Exception):
    pass


def _virtual_pages(text: str) -> list[str]:
    if len(text) <= VIRTUAL_PAGE_CHARS:
        return [text]
    pages: list[str] = []
    paragraphs = text.split("\n")
    buf: list[str] = []
    size = 0
    for para in paragraphs:
        buf.append(para)
        size += len(para) + 1
        if size >= VIRTUAL_PAGE_CHARS:
            pages.append("\n".join(buf))
            buf, size = [], 0
    if buf:
        pages.append("\n".join(buf))
    return pages


def extract_pages(path: Path, mime: str) -> list[str]:
    """Return one text string per (real or virtual) page."""
    suffix = path.suffix.lower()
    if suffix == ".pdf" or mime == "application/pdf":
        pages: list[str] = []
        with pymupdf.open(path) as doc:
            for page in doc:
                pages.append(page.get_text("text"))
        if not pages or not any(p.strip() for p in pages):
            raise UnsupportedFileError(
                "No extractable text — the PDF may be a scanned image (OCR is not supported yet)."
            )
        return pages
    if suffix == ".docx" or "wordprocessingml" in mime:
        d = DocxDocument(str(path))
        text = "\n".join(p.text for p in d.paragraphs)
        return _virtual_pages(text)
    if suffix in (".txt", ".md") or mime.startswith("text/"):
        return _virtual_pages(path.read_text(encoding="utf-8", errors="replace"))
    raise UnsupportedFileError(f"Unsupported file type '{suffix or mime}'")


def is_supported(filename: str) -> bool:
    return Path(filename).suffix.lower() in SUPPORTED_EXTENSIONS
