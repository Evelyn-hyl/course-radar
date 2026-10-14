from __future__ import annotations

# pyright: strict

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

import pymupdf4llm


class _PyMuPdf4Llm(Protocol):
    def to_markdown(
        self,
        document: str | Path,
        *,
        page_chunks: bool,
        show_progress: bool,
    ) -> object: ...


_pymupdf4llm = cast(_PyMuPdf4Llm, pymupdf4llm)


class PdfChunkingError(RuntimeError):
    """Raised when PyMuPDF4LLM cannot turn a PDF into usable chunks."""


@dataclass(frozen=True, slots=True)
class DocumentChunk:
    text: str
    page_start: int
    page_end: int
    section_path: tuple[str, ...] = ()
    content_types: tuple[str, ...] = ()


def chunk_pdf(
    pdf_path: str | Path,
) -> tuple[DocumentChunk, ...]:
    """Extract a PDF as layout-aware Markdown chunks, one per page."""

    path = Path(pdf_path)

    if not path.is_file():
        raise FileNotFoundError(f"PDF does not exist: {path}")
    
    try:
        raw_page_chunks = _pymupdf4llm.to_markdown(
            path,
            page_chunks=True,
            show_progress=False,
        )
    except Exception as error:
        raise PdfChunkingError(f"Could not chunk PDF: {path.name}") from error

    if not isinstance(raw_page_chunks, list):
        raise PdfChunkingError("PyMuPDF4LLM returned an unexpected result.")

    page_chunks = cast(list[object], raw_page_chunks)
    chunks = tuple(
        chunk
        for raw_chunk in page_chunks
        if (chunk := _normalize_page_chunk(raw_chunk)) is not None
    )

    if not chunks:
        raise PdfChunkingError(f"PDF contains no extractable content: {path.name}")
    
    return chunks


def _normalize_page_chunk(raw_chunk: object) -> DocumentChunk | None:
    if not isinstance(raw_chunk, dict):
        raise PdfChunkingError("PyMuPDF4LLM returned an invalid page chunk.")

    chunk = cast(dict[str, object], raw_chunk)
    text = chunk.get("text")
    raw_metadata = chunk.get("metadata")

    if not isinstance(text, str) or not isinstance(raw_metadata, dict):
        raise PdfChunkingError("PyMuPDF4LLM returned an invalid page chunk.")

    metadata = cast(dict[str, object], raw_metadata)
    page_number = metadata.get("page_number")

    if not isinstance(page_number, int) or isinstance(page_number, bool):
        raise PdfChunkingError("Page chunk is missing a valid page number.")

    normalized_text = text.strip()
    
    if not normalized_text:
        return None

    return DocumentChunk(
        text=normalized_text,
        page_start=page_number,
        page_end=page_number,
    )
