from uuid import uuid4
from unittest import TestCase
from unittest.mock import MagicMock

from sqlalchemy.orm import Session

from app.ingestion.chunker import DocumentChunk
from app.repositories.documents import DocumentRepository


class DocumentRepositoryTests(TestCase):
    def test_adds_chunks_with_embeddings_and_model(self) -> None:
        session = MagicMock(spec=Session)
        document_id = uuid4()
        chunk = DocumentChunk(text="Conditional probability", page_start=4, page_end=4)

        records = DocumentRepository(session).add_chunks(
            document_id=document_id,
            chunks=[chunk],
            embeddings=[[0.1, 0.2, 0.3]],
        )

        self.assertEqual(len(records), 1)
        self.assertEqual(records[0].document_id, document_id)
        self.assertEqual(records[0].text, chunk.text)
        self.assertEqual(records[0].embedding, [0.1, 0.2, 0.3])
        self.assertEqual(records[0].embedding_model, "google/embeddinggemma-300m")
        session.add_all.assert_called_once_with(records)

    def test_rejects_mismatched_chunk_and_embedding_counts(self) -> None:
        session = MagicMock(spec=Session)

        with self.assertRaises(ValueError):
            DocumentRepository(session).add_chunks(
                document_id=uuid4(),
                chunks=[DocumentChunk(text="Text", page_start=1, page_end=1)],
                embeddings=[],
            )
