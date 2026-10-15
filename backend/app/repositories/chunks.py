from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Chunk, Document


@dataclass(frozen=True, slots=True)
class ChunkCandidate:
    chunk: Chunk
    document_title: str
    distance: float


class ChunkRepository:
    def __init__(self, session: Session) -> None:
        self._session = session
    
    def find_similar(
        self,
        *,
        course_id: UUID,
        embedding: list[float],
        limit: int = 5,
    ) -> list[ChunkCandidate]:
        distance = Chunk.embedding.cosine_distance(embedding)

        statement = (
            select(
                Chunk,
                Document.title,
                distance.label("distance"),
            )
            .join(Document, Chunk.document_id == Document.id)
            .where(
                Document.course_id == course_id,
                Chunk.embedding.is_not(None),
            )
            .order_by(distance)
            .limit(limit)
        )

        rows = self._session.execute(statement).all()

        return [
            ChunkCandidate(
                chunk=chunk,
                document_title=document_title,
                distance=float(distance_value),
            )
            for chunk, document_title, distance_value in rows
        ]
