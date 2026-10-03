"""Structure-aware splitting of legal documents into sections and chunks.

Recognizes legal numbering ("ARTICLE 7", "8.2 Indemnification", ALL-CAPS
headings), builds hierarchical section paths, and packs sections into
overlapping token-bounded chunks. Chunk/section page ranges come from the
page layout returned by extraction, so citations can point at real pages.
"""

import re
from bisect import bisect_right
from dataclasses import dataclass

_TINY_TOKENS = 40


@dataclass
class Section:
    section_path: str
    text: str
    start: int  # absolute char offset in the joined page text
    end: int
    page_start: int
    page_end: int


@dataclass
class ChunkData:
    section_path: str
    text: str
    page_start: int
    page_end: int


_NUMBER_HEADING = re.compile(r"^(\d+(?:\.\d+){0,3})[\.\):]?\s+\S")
_WORD_HEADING = re.compile(r"^(article|section)\s+\S+", re.IGNORECASE)
_CAPS_HEADING = re.compile(r"^[A-Z][A-Z \-&,'()/]{2,79}$")
_MAX_HEADING_LEN = 120


def _classify_heading(line: str) -> tuple[int, str] | None:
    """Return (depth, path_label) if the line looks like a heading."""
    if not line or len(line) > _MAX_HEADING_LEN:
        return None
    m = _NUMBER_HEADING.match(line)
    if m:
        return m.group(1).count(".") + 1, line.strip()
    if _WORD_HEADING.match(line):
        return 1, line.strip()
    if _CAPS_HEADING.match(line):
        return 1, line.strip()
    return None


def _join_pages(pages: list[str]) -> tuple[str, list[int]]:
    """Join pages with a separator; return the text and each page's start
    offset (pages are numbered from 1)."""
    starts: list[int] = []
    parts: list[str] = []
    offset = 0
    for i, ptext in enumerate(pages, start=1):
        starts.append(offset)
        parts.append(ptext)
        offset += len(ptext) + 2  # "\n\n" separator
    return "\n\n".join(parts), starts


def parse_sections(pages: list[str]) -> list[Section]:
    full, page_starts = _join_pages(pages)

    def page_of(offset: int) -> int:
        if not page_starts:
            return 1
        idx = bisect_right(page_starts, offset) - 1
        return idx + 1 if idx >= 0 else 1

    headings: list[tuple[int, int, str]] = []  # (offset, depth, label)
    pos = 0
    for line in full.splitlines(keepends=True):
        line_start = pos
        pos += len(line)
        classified = _classify_heading(line.strip())
        if classified:
            depth, label = classified
            headings.append((line_start, depth, label))

    def make_section(path: str, start: int, end: int) -> Section:
        return Section(path, full[start:end], start, end, page_of(start), page_of(end))

    if not headings:
        return [make_section("", 0, len(full))] if full.strip() else []

    sections: list[Section] = []
    if headings[0][0] > 0 and full[: headings[0][0]].strip():
        sections.append(make_section("", 0, headings[0][0]))

    stack: list[str] = []
    for i, (offset, depth, label) in enumerate(headings):
        del stack[depth - 1 :]
        stack.append(label)
        start = offset
        end = headings[i + 1][0] if i + 1 < len(headings) else len(full)
        sections.append(make_section(" > ".join(stack), start, end))
    return sections


def _windows(text: str, max_chars: int, overlap_chars: int) -> list[tuple[int, int]]:
    """Cover text with (start, end) windows of <= max_chars, preferring to cut
    at line breaks and overlapping consecutive windows."""
    windows: list[tuple[int, int]] = []
    pos = 0
    n = len(text)
    while pos < n:
        end = min(pos + max_chars, n)
        if end < n:
            nl = text.rfind("\n", pos + int(max_chars * 0.5), end)
            if nl > pos:
                end = nl + 1
        windows.append((pos, end))
        if end >= n:
            break
        pos = max(end - overlap_chars, pos + 1)
    return windows


def build_chunks(
    pages: list[str], *, max_tokens: int = 700, overlap_tokens: int = 100
) -> list[ChunkData]:
    """Pack parsed sections into token-bounded chunks (1 token ~= 4 chars).
    Tiny sections are merged into the chunk that follows them."""
    max_chars = max_tokens * 4
    overlap_chars = overlap_tokens * 4
    _, page_starts = _join_pages(pages)

    def page_of(offset: int) -> int:
        if not page_starts:
            return 1
        idx = bisect_right(page_starts, offset) - 1
        return idx + 1 if idx >= 0 else 1

    chunks: list[ChunkData] = []
    pending: dict | None = None  # text from tiny sections waiting to be merged

    def flush(item: dict | None) -> None:
        if item and item["text"].strip():
            chunks.append(
                ChunkData(
                    section_path=item["section_path"],
                    text=item["text"].strip(),
                    page_start=item["page_start"],
                    page_end=item["page_end"],
                )
            )

    for section in parse_sections(pages):
        text = section.text
        if not text.strip():
            continue
        tokens = len(text) // 4

        if tokens <= _TINY_TOKENS:
            if pending:
                pending["text"] += "\n\n" + text
                pending["page_end"] = section.page_end
            else:
                pending = {
                    "section_path": section.section_path,
                    "text": text,
                    "page_start": section.page_start,
                    "page_end": section.page_end,
                }
            continue

        if tokens <= max_tokens:
            if pending:
                flush(
                    {
                        "section_path": section.section_path,
                        "text": pending["text"] + "\n\n" + text,
                        "page_start": pending["page_start"],
                        "page_end": section.page_end,
                    }
                )
                pending = None
            else:
                flush(
                    {
                        "section_path": section.section_path,
                        "text": text,
                        "page_start": section.page_start,
                        "page_end": section.page_end,
                    }
                )
            continue

        # oversized section: emit overlapping windows, prepending any pending text
        for i, (w_start, w_end) in enumerate(_windows(text, max_chars, overlap_chars)):
            piece = text[w_start:w_end]
            if i == 0 and pending:
                piece = pending["text"] + "\n\n" + piece
                page_start = pending["page_start"]
                pending = None
            else:
                page_start = page_of(section.start + w_start)
            flush(
                {
                    "section_path": section.section_path,
                    "text": piece,
                    "page_start": page_start,
                    "page_end": page_of(section.start + w_end - 1),
                }
            )

    flush(pending)
    return chunks
