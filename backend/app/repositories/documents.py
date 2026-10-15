from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.orm import Session

from app.db.models import Chunk
from app.embeddings.constants import EMBEDDING_MODEL
from app.ingestion.chunker import DocumentChunk


class DocumentRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add_chunks(
        self,
        *,
        document_id: UUID,
        chunks: Sequence[DocumentChunk],
        embeddings: Sequence[list[float]],
        embedding_model: str = EMBEDDING_MODEL,
    ) -> list[Chunk]:
        if len(chunks) != len(embeddings):
            raise ValueError("Every chunk must have exactly one embedding.")

        records = [
            Chunk(
                document_id=document_id,
                content_type=None,
                chapter_label=None,
                chapter_title=None,
                section_label=None,
                section_title=None,
                page_start=chunk.page_start,
                page_end=chunk.page_end,
                text=chunk.text,
                embedding=embedding,
                embedding_model=embedding_model,
            )
            for chunk, embedding in zip(chunks, embeddings, strict=True)
        ]
        self._session.add_all(records)
        return records
