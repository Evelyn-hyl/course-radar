from typing import Annotated
from uuid import UUID

from fastapi import Depends
from sqlalchemy.orm import Session

from app.answer_generation.client import (
    AnswerContext,
    AnswerGenerator,
    get_answer_generator,
)
from app.db.models import Course
from app.db.session import get_session
from app.embeddings.client import EmbeddingClient, get_embedding_client
from app.repositories.chunks import ChunkCandidate, ChunkRepository
from app.schemas.answers import AnswerCitation, AnswerResponse


RETRIEVAL_LIMIT = 5
NO_CONTEXT_ANSWER = "I couldn't find an answer in the available course material."


class AnswerCourseNotFoundError(LookupError):
    """Raised when an answer is requested for a course that does not exist."""


class AnswerService:
    def __init__(
        self,
        *,
        session: Session,
        chunk_repository: ChunkRepository,
        embedding_client: EmbeddingClient,
        answer_generator: AnswerGenerator,
    ) -> None:
        self._session = session
        self._chunks = chunk_repository
        self._embeddings = embedding_client
        self._generator = answer_generator

    async def answer(self, *, course_id: UUID, question: str) -> AnswerResponse:
        normalized_question = question.strip()
        if not normalized_question:
            raise ValueError("Question cannot be empty.")
        if self._session.get(Course, course_id) is None:
            raise AnswerCourseNotFoundError(f"Course does not exist: {course_id}")

        query_embedding = await self._embeddings.embed_query(normalized_question)
        candidates = self._chunks.find_similar(
            course_id=course_id,
            embedding=query_embedding,
            limit=RETRIEVAL_LIMIT,
        )

        if not candidates:
            return AnswerResponse(answer=NO_CONTEXT_ANSWER, citations=[])

        generated = await self._generator.generate(
            question=normalized_question,
            contexts=[
                AnswerContext(source_id=index, text=candidate.chunk.text)
                for index, candidate in enumerate(candidates, start=1)
            ],
        )

        citations = self._build_citations(
            candidates,
            generated.cited_source_ids,
        )
        return AnswerResponse(answer=generated.answer, citations=citations)

    @staticmethod
    def _build_citations(
        candidates: list[ChunkCandidate],
        cited_source_ids: tuple[int, ...],
    ) -> list[AnswerCitation]:
        candidate_by_source_id = {
            index: candidate
            for index, candidate in enumerate(candidates, start=1)
        }

        return [
            AnswerCitation(
                chunk_id=candidate.chunk.id,
                document_id=candidate.chunk.document_id,
                document_title=candidate.document_title,
                page_start=candidate.chunk.page_start,
                page_end=candidate.chunk.page_end,
            )
            for source_id in cited_source_ids
            if (candidate := candidate_by_source_id.get(source_id)) is not None
        ]


def get_answer_service(
    session: Annotated[Session, Depends(get_session)],
    embedding_client: Annotated[
        EmbeddingClient,
        Depends(get_embedding_client),
    ],
    answer_generator: Annotated[
        AnswerGenerator,
        Depends(get_answer_generator),
    ],
) -> AnswerService:
    return AnswerService(
        session=session,
        chunk_repository=ChunkRepository(session),
        embedding_client=embedding_client,
        answer_generator=answer_generator,
    )
