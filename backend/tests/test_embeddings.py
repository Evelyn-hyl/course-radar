from unittest import IsolatedAsyncioTestCase
from unittest.mock import MagicMock

import numpy as np

from app.embeddings.client import EmbeddingGenerationError, EmbeddingGemmaClient


class EmbeddingGemmaClientTests(IsolatedAsyncioTestCase):
    async def test_batches_inputs_and_preserves_input_order(self) -> None:
        model = MagicMock()
        model.encode_document.side_effect = [
            np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]),
            np.array([[7.0, 8.0, 9.0]]),
        ]
        client = EmbeddingGemmaClient(model, dimensions=3, batch_size=2)

        result = await client.embed_documents(["one", "two", "three"])

        self.assertEqual(
            result,
            [
                [1.0, 2.0, 3.0],
                [4.0, 5.0, 6.0],
                [7.0, 8.0, 9.0],
            ],
        )
        self.assertEqual(model.encode_document.call_count, 2)
        model.encode_document.assert_any_call(
            ["one", "two"],
            batch_size=2,
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

    async def test_rejects_an_embedding_with_wrong_dimensions(self) -> None:
        model = MagicMock()
        model.encode_document.return_value = np.array([[1.0, 2.0]])
        client = EmbeddingGemmaClient(model, dimensions=3)

        with self.assertRaises(EmbeddingGenerationError):
            await client.embed_documents(["one"])

    async def test_rejects_empty_text(self) -> None:
        client = EmbeddingGemmaClient(MagicMock(), dimensions=3)

        with self.assertRaises(ValueError):
            await client.embed_documents([" "])

    async def test_embeds_a_query(self) -> None:
        model = MagicMock()
        model.encode_query.return_value = np.array([1.0, 2.0, 3.0])
        client = EmbeddingGemmaClient(model, dimensions=3)

        result = await client.embed_query("conditional probability")

        self.assertEqual(result, [1.0, 2.0, 3.0])
        model.encode_query.assert_called_once_with(
            "conditional probability",
            normalize_embeddings=True,
            convert_to_numpy=True,
            show_progress_bar=False,
        )

    async def test_rejects_empty_query(self) -> None:
        client = EmbeddingGemmaClient(MagicMock(), dimensions=3)

        with self.assertRaises(ValueError):
            await client.embed_query(" ")

    async def test_wraps_model_errors(self) -> None:
        model = MagicMock()
        model.encode_document.side_effect = RuntimeError("model failed")
        client = EmbeddingGemmaClient(model, dimensions=3)

        with self.assertRaisesRegex(
            EmbeddingGenerationError,
            "Local embedding generation failed",
        ):
            await client.embed_documents(["one"])
