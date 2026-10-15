import asyncio
from collections.abc import Sequence
from functools import lru_cache
from typing import TYPE_CHECKING, Protocol, cast

import numpy as np
from numpy.typing import NDArray

if TYPE_CHECKING:
    from sentence_transformers import SentenceTransformer

from app.db.config import load_backend_environment
from app.embeddings.constants import (
    EMBEDDING_BATCH_SIZE,
    EMBEDDING_DIMENSIONS,
    EMBEDDING_MODEL,
)


class EmbeddingGenerationError(RuntimeError):
    """Raised when embeddings cannot be generated or validated."""


class EmbeddingClient(Protocol):
    model: str
    dimensions: int

    async def embed_documents(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]: ...

    async def embed_query(self, text: str) -> list[float]: ...


class EmbeddingGemmaClient:
    def __init__(
        self,
        model_client: "SentenceTransformer",
        *,
        model: str = EMBEDDING_MODEL,
        dimensions: int = EMBEDDING_DIMENSIONS,
        batch_size: int = EMBEDDING_BATCH_SIZE,
    ) -> None:
        if dimensions <= 0:
            raise ValueError("dimensions must be greater than zero")
        if batch_size <= 0:
            raise ValueError("batch_size must be greater than zero")

        self._model_client = model_client
        self.model = model
        self.dimensions = dimensions
        self._batch_size = batch_size

    async def embed_documents(self, texts: Sequence[str]) -> list[list[float]]:
        if any(not text.strip() for text in texts):
            raise ValueError("Embedding inputs cannot be empty.")

        embeddings: list[list[float]] = []

        for start in range(0, len(texts), self._batch_size):
            batch = list(texts[start : start + self._batch_size])

            try:
                batch_embeddings = await asyncio.to_thread(
                    self._encode_batch,
                    batch,
                )
            except Exception as error:
                raise EmbeddingGenerationError(
                    "Local embedding generation failed."
                ) from error

            if len(batch_embeddings) != len(batch):
                raise EmbeddingGenerationError(
                    "The embedding model returned an unexpected number of vectors."
                )

            for vector in batch_embeddings:
                if len(vector) != self.dimensions:
                    raise EmbeddingGenerationError(
                        "The embedding model returned an unexpected vector size."
                    )
                embeddings.append(vector)

        return embeddings

    async def embed_query(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Embedding query cannot be empty.")

        try:
            embedding = await asyncio.to_thread(
                self._encode_query,
                text,
            )
        except Exception as error:
            raise EmbeddingGenerationError(
                "Local query embedding generation failed."
            ) from error

        if len(embedding) != self.dimensions:
            raise EmbeddingGenerationError(
                "The embedding model returned an unexpected vector size."
            )

        return embedding

    def _encode_query(self, text: str) -> list[float]:
        result = cast(
            NDArray[np.float32],
            self._model_client.encode_query(  # pyright: ignore[reportUnknownMemberType]
                text,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            ),
        )
        return result.tolist()

    def _encode_batch(self, texts: list[str]) -> list[list[float]]:
        result = cast(
            NDArray[np.float32],
            self._model_client.encode_document(  # pyright: ignore[reportUnknownMemberType]
                texts,
                batch_size=self._batch_size,
                normalize_embeddings=True,
                convert_to_numpy=True,
                show_progress_bar=False,
            ),
        )
        return result.tolist()


@lru_cache(maxsize=1)
def get_embedding_client() -> EmbeddingClient:
    from sentence_transformers import SentenceTransformer

    load_backend_environment()
    model = SentenceTransformer(EMBEDDING_MODEL)
    return EmbeddingGemmaClient(model)
