"""use embeddinggemma vectors

Revision ID: 8f3c24a7b190
Revises: 3d9080c0d015
Create Date: 2026-10-14

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector


revision: str = "8f3c24a7b190"
down_revision: str | None = "3d9080c0d015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Vectors from the previous model are incompatible with EmbeddingGemma.
    op.execute(sa.text("UPDATE chunks SET embedding = NULL, embedding_model = NULL"))
    op.alter_column(
        "chunks",
        "embedding",
        existing_type=Vector(1536),
        type_=Vector(768),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.execute(sa.text("UPDATE chunks SET embedding = NULL, embedding_model = NULL"))
    op.alter_column(
        "chunks",
        "embedding",
        existing_type=Vector(768),
        type_=Vector(1536),
        existing_nullable=True,
    )
