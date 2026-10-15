from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.embeddings.client import EmbeddingClient, get_embedding_client
from app.repositories.chunks import ChunkRepository
from app.schemas.retrieval import ChunkSearchResult, RetrievalResponse


class RetrievalService:
    def __init__(
        self,
        chunk_repository: ChunkRepository,
        embedding_client: EmbeddingClient,
        session: Session,
    ) -> None:
        self._chunks = chunk_repository
        self._embeddings = embedding_client
        self._session = session

    async def search(
        self,
        *,
        course_id: UUID,
        query: str,
        limit: int = 5,
    ) -> RetrievalResponse:
        query_embedding = await self._embeddings.embed_query(query)

        candidates = self._chunks.find_similar(
            course_id=course_id,
            embedding=query_embedding,
            limit=limit * 2,
        )

        results = [
            ChunkSearchResult(
                chunk_id=candidate.chunk.id,
                document_id=candidate.chunk.document_id,
                document_title=candidate.document_title,
                text=candidate.chunk.text,
                page_start=candidate.chunk.page_start,
                page_end=candidate.chunk.page_end,
                chapter_label=candidate.chunk.chapter_label,
                chapter_title=candidate.chunk.chapter_title,
                section_label=candidate.chunk.section_label,
                section_title=candidate.chunk.section_title,
                distance=candidate.distance,
            )
            for candidate in candidates
        ][:limit]
        

        return RetrievalResponse(results=results)


def get_retrieval_service(
    session: Annotated[Session, Depends(get_session)],
    embedding_client: Annotated[
        EmbeddingClient,
        Depends(get_embedding_client),
    ],
) -> RetrievalService:
    return RetrievalService(
        session=session,
        chunk_repository=ChunkRepository(session),
        embedding_client=embedding_client,
    )