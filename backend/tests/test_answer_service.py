from types import SimpleNamespace
from typing import cast
from unittest import IsolatedAsyncioTestCase
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from sqlalchemy.orm import Session

from app.answer_generation.client import AnswerGenerator, GeneratedAnswer
from app.db.models import Chunk, Course
from app.embeddings.client import EmbeddingClient
from app.repositories.chunks import ChunkCandidate
from app.services.answers import AnswerService, NO_CONTEXT_ANSWER, RETRIEVAL_LIMIT


class AnswerServiceTests(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.course_id = uuid4()
        self.session = MagicMock(spec=Session)
        self.session.get.return_value = Course(id=self.course_id, name="MATH 154")
        self.repository = MagicMock()
        self.embed_query = AsyncMock(return_value=[0.1, 0.2, 0.3])
        self.embedding_client = cast(
            EmbeddingClient,
            SimpleNamespace(
                model="test-model",
                dimensions=3,
                embed_documents=AsyncMock(),
                embed_query=self.embed_query,
            ),
        )
        self.generate = AsyncMock()
        self.generator = cast(
            AnswerGenerator,
            SimpleNamespace(generate=self.generate),
        )
        self.service = AnswerService(
            session=self.session,
            chunk_repository=self.repository,
            embedding_client=self.embedding_client,
            answer_generator=self.generator,
        )

    async def test_generates_an_answer_and_maps_valid_source_ids(self) -> None:
        first = self._candidate(page=26, title="Week 2", distance=0.20)
        second = self._candidate(page=29, title="Week 2", distance=0.25)
        self.repository.find_similar.return_value = [first, second]
        self.generate.return_value = GeneratedAnswer(
            answer="Dirac's theorem gives a sufficient degree condition.",
            cited_source_ids=(2, 99),
        )

        response = await self.service.answer(
            course_id=self.course_id,
            question="What is Dirac's theorem?",
        )

        self.repository.find_similar.assert_called_once_with(
            course_id=self.course_id,
            embedding=[0.1, 0.2, 0.3],
            limit=RETRIEVAL_LIMIT,
        )
        self.assertEqual(len(response.citations), 1)
        self.assertEqual(response.citations[0].chunk_id, second.chunk.id)
        self.generate.assert_awaited_once()
        await_args = self.generate.await_args
        assert await_args is not None
        contexts = await_args.kwargs["contexts"]
        self.assertEqual([context.source_id for context in contexts], [1, 2])

    async def test_returns_a_fallback_without_calling_generator(self) -> None:
        self.repository.find_similar.return_value = []

        response = await self.service.answer(
            course_id=self.course_id,
            question="Unknown topic",
        )

        self.assertEqual(response.answer, NO_CONTEXT_ANSWER)
        self.assertEqual(response.citations, [])
        self.generate.assert_not_awaited()

    @staticmethod
    def _candidate(*, page: int, title: str, distance: float) -> ChunkCandidate:
        return ChunkCandidate(
            chunk=Chunk(
                id=uuid4(),
                document_id=uuid4(),
                page_start=page,
                page_end=page,
                text=f"Source text from page {page}",
            ),
            document_title=title,
            distance=distance,
        )
