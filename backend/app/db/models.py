from datetime import datetime
import uuid
from enum import Enum as PythonEnum

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, Enum as SqlEnum, func, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.domain.documents import SourceType, DocumentStatus, ChunkContentType, ConceptType, ExampleConceptRelationship, VerificationStatus, ExtractionStatus
from app.embeddings.constants import EMBEDDING_DIMENSIONS

def enum_values(enum_type: type[PythonEnum]) -> list[str]:
    return [str(item.value) for item in enum_type]


class Base(DeclarativeBase):
    pass

class Course(Base):
    __tablename__ = "courses"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255))

class Document(Base):
    __tablename__ = "documents"
    __table_args__= (
        UniqueConstraint(
            "course_id",
            "checksum",
            name="uq_course_document_checksum",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    course_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("courses.id")
    )
    title: Mapped[str] = mapped_column(String(255))
    source_type: Mapped[SourceType] = mapped_column(
        SqlEnum(
            SourceType,
            name="source_type",
            values_callable=enum_values,
        )
    )
    path: Mapped[str] = mapped_column(Text)
    checksum: Mapped[str] = mapped_column(String(64))
    status: Mapped[DocumentStatus] = mapped_column(
        SqlEnum(
            DocumentStatus,
            name="document_status",
            values_callable=enum_values,
        ),
        default=DocumentStatus.PENDING,
    )
    week: Mapped[int | None]
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

class DocumentPage(Base):
    __tablename__ = "document_pages"
    __table_args__ = (
        UniqueConstraint(
            "document_id",
            "page_number",
            name="uq_document_page_number",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )
    page_number: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    layout_blocks: Mapped[list[dict[str, object]]] = mapped_column(
        JSONB,
        default=list,
    )
    extraction_status: Mapped[ExtractionStatus] = mapped_column(
        SqlEnum(
            ExtractionStatus,
            name="extraction_status",
            values_callable=enum_values,
        )
    )

class DocumentExtractionWarning(Base):
    __tablename__ = "document_extraction_warnings"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )
    code: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(Text)
    page_number: Mapped[int | None] = mapped_column(Integer)

class Chunk(Base):
    __tablename__ = "chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("documents.id", ondelete="CASCADE"),
        index=True,
    )
    content_type: Mapped[ChunkContentType | None] = mapped_column(
        SqlEnum(
            ChunkContentType,
            name="chunk_content_type",
            values_callable=enum_values,
        )
    )
    chapter_label: Mapped[str | None]
    chapter_title: Mapped[str | None]
    section_label: Mapped[str | None]
    section_title: Mapped[str | None]
    page_start: Mapped[int] = mapped_column(Integer)
    page_end: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list[float] | None] = mapped_column(
        Vector(EMBEDDING_DIMENSIONS),
        nullable=True,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

class Concept(Base):
    __tablename__ = "concepts"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chunks.id"), index=True
    )
    concept_type: Mapped[ConceptType] = mapped_column(
        SqlEnum(
            ConceptType,
            name="concept_type",
            values_callable=enum_values,
        )
    )
    label: Mapped[str | None] = mapped_column(String(100))
    name: Mapped[str | None] = mapped_column(String(255))
    conclusion: Mapped[str] = mapped_column(Text)
    conditions: Mapped[list[str]] = mapped_column(
        JSONB, default=list
    )

class Example(Base):
    __tablename__ = "examples"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("chunks.id"),
        index=True,
    )
    label: Mapped[str | None] = mapped_column(String(100))
    problem_text: Mapped[str] = mapped_column(Text)
    solution_text: Mapped[str | None] = mapped_column(Text)

class ExampleConceptLink(Base):
    __tablename__ = "example_concept_links"
    __table_args__ = (
        UniqueConstraint(
            "example_id",
            "concept_id",
            name="uq_example_concept_link",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4,
    )
    example_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("examples.id", ondelete="CASCADE"),
        index=True,
    )
    concept_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("concepts.id", ondelete="CASCADE"),
        index=True,
    )
    relationship: Mapped[ExampleConceptRelationship] = mapped_column(
        SqlEnum(
            ExampleConceptRelationship,
            name="example_concept_relationship",
            values_callable=enum_values,
        )
    )
    evidence_chunk_id: Mapped[uuid.UUID | None] = mapped_column(
        ForeignKey("chunks.id"),
    )
    evidence_excerpt: Mapped[str | None] = mapped_column(Text)
    verification_status: Mapped[VerificationStatus] = mapped_column(
        SqlEnum(
            VerificationStatus,
            name="verification_status",
            values_callable=enum_values,
        )
    )
    classifier_name: Mapped[str | None] = mapped_column(String(100))
    classifier_version: Mapped[str | None] = mapped_column(String(100))
