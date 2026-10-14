from dataclasses import dataclass
from pathlib import Path

from app.ingestion.chunker import DocumentChunk, chunk_pdf


@dataclass(frozen=True, slots=True)
class IngestionResult:
    chunks: tuple[DocumentChunk, ...]
    page_count: int


def ingest_pdf(pdf_path: str | Path) -> IngestionResult:
    """Run the extraction/chunking portion of document ingestion."""
    chunks = chunk_pdf(pdf_path)
    return IngestionResult(
        chunks=chunks,
        page_count=max(chunk.page_end for chunk in chunks),
    )
