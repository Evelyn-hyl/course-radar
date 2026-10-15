from uuid import UUID

from pydantic import BaseModel


class ChunkSearchResult(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_title: str
    text: str
    page_start: int
    page_end: int
    chapter_label: str | None = None
    chapter_title: str | None = None
    section_label: str | None = None
    section_title: str | None = None
    distance: float

class RetrievalResponse(BaseModel):
    results: list[ChunkSearchResult]