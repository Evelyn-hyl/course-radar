from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID

from app.domain.documents import SourceType, DocumentStatus, ChunkContentType, ConceptType, ExtractionStatus

# ==============================================================================
#  SHARED
# ==============================================================================

class ExtractionWarning(BaseModel):
    code: str
    message: str
    page_number: int | None = None

def empty_extraction_warnings() -> list[ExtractionWarning]:
    return []

class ExtractedItemSummary(BaseModel):
    id: UUID
    chunk_id: UUID
    content_type: ChunkContentType
    label: str | None = None
    title: str | None = None
    excerpt: str
    page_start: int
    page_end: int

class ErrorResponse(BaseModel):
    code: str
    message: str
    details: dict[str, str] = Field(default_factory=dict)

class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    source_type: SourceType
    status: DocumentStatus
    week: int | None
    created_at: datetime

# ==============================================================================
#  DOCUMENT QUERIES
# ==============================================================================

class DocumentListResponse(BaseModel):
    documents: list[DocumentResponse]

class DocumentDetailResponse(BaseModel):
    document: DocumentResponse
    page_count: int
    chunk_count: int
    items: list[ExtractedItemSummary]
    warnings: list[ExtractionWarning]

class DocumentPageResponse(BaseModel):
    document_id: UUID
    page_number: int
    text: str
    extraction_status: ExtractionStatus
    warnings: list[ExtractionWarning] = Field(
        default_factory=empty_extraction_warnings
    )

# ==============================================================================
#  INGESTION
# ==============================================================================

class IngestionResponse(BaseModel):
    document: DocumentResponse
    page_count: int
    chunk_count: int
    items: list[ExtractedItemSummary]
    warnings: list[ExtractionWarning]


class IngestedChunkResponse(BaseModel):
    text: str
    page_start: int
    page_end: int
    section_path: list[str] = Field(default_factory=list)
    content_types: list[str] = Field(default_factory=list)


class IngestionPreviewResponse(BaseModel):
    """Temporary response used before document persistence is implemented."""

    page_count: int
    chunk_count: int
    chunks: list[IngestedChunkResponse]

class DocumentUploadMetadata(BaseModel):
    course_id: UUID
    title: str = Field(min_length=1, max_length=255)
    source_type: SourceType
    week: int | None = Field(default=None, ge=1)

# ==============================================================================
#  SOURCE REFERENCES
# ==============================================================================

class SourceReferenceResponse(BaseModel):
    chunk_id: UUID
    document_id: UUID
    chapter_label: str | None = None
    chapter_title: str | None = None
    section_label: str | None = None
    section_title: str | None = None
    page_start: int
    page_end: int

class SourceExcerptResponse(SourceReferenceResponse):
    text: str

# ==============================================================================
#  CONCEPT RESPONSES
# ==============================================================================

class ConceptBase(BaseModel):
    id: UUID
    concept_type: ConceptType
    label: str | None = None
    name: str | None = None
    conclusion: str
    conditions: list[str] = Field(default_factory=list)

class ConceptResponse(ConceptBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "5d4d59ba-a1f1-4e40-b967-98984717ec1f",
                    "concept_type": "theorem",
                    "label": "Theorem 1.42",
                    "name": "Bayes' rule",
                    "conclusion": "For every $j \\in \\{1, \\ldots, n\\}$,\n\n$$P(B_j \\mid A) = \\frac{P(B_j)P(A \\mid B_j)}{\\sum_{i=1}^{n} P(B_i)P(A \\mid B_i)}.$$",
                    "conditions": [
                        "$B_1, B_2, \\ldots, B_n$ is a finite partition of $\\Omega$.",
                        "$P(B_i) > 0$ for every $i \\in \\{1, \\ldots, n\\}$.",
                        "$A$ is an event with $P(A) > 0$."
                    ],
                    "source": {
                        "chunk_id": "3f10b71e-cd34-4a29-b738-797512684528",
                        "document_id": "6502ef94-c9a7-41c7-8b36-5c7bb094d7b9",
                        "page_start": 38,
                        "page_end": 38
                    }
                },
                {
                    "id": "8f80f77a-a777-4ff8-9ca9-2851a824d315",
                    "concept_type": "proposition",
                    "label": "Proposition 1.12",
                    "name": "Addition Rule",
                    "conclusion": "$$P(A \\cup B) = P(A) + P(B) - P(A \\cap B).$$",
                    "conditions": [
                        "$A$ and $B$ are events."
                    ],
                    "source": {
                        "chunk_id": "67c5c876-f1b8-4dc6-a520-6f80f33c47dd",
                        "document_id": "6502ef94-c9a7-41c7-8b36-5c7bb094d7b9",
                        "page_start": 13,
                        "page_end": 13
                    }
                }
            ]
        }
    )

    source: SourceReferenceResponse

class ConceptDetailResponse(ConceptBase):
    source: SourceExcerptResponse

# ==============================================================================
#  WORKED-EXAMPLES RESPONSES
# ==============================================================================

class ExampleBase(BaseModel):
    id: UUID
    label: str | None = None
    problem_text: str
    solution_text: str | None = None

class ExampleResponse(ExampleBase):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "id": "34efc6d1-6939-4328-bb76-da765ee20e02",
                    "label": "Example 1.18",
                    "problem_text": "In the United States, $45\\%$ of people own a dog, $29\\%$ own a cat, and $15\\%$ own both a dog and a cat. If a person owns a dog, what is the probability that the person also owns a cat?",
                    "solution_text": "Choose a person from the United States at random. Let $C$ be the event that the person owns a cat, and let $D$ be the event that the person owns a dog. Because the person owns a dog, compute $P(C \\mid D)$. Using the definition of conditional probability,\n\n$$P(C \\mid D) = \\frac{P(C \\cap D)}{P(D)} = \\frac{0.15}{0.45} \\approx 0.333.$$",
                    "source": {
                        "chunk_id": "a82def15-e94b-4ba0-954d-c38003601e84",
                        "document_id": "6502ef94-c9a7-41c7-8b36-5c7bb094d7b9",
                        "page_start": 19,
                        "page_end": 19
                    }
                }
            ]
        }
    )

    source: SourceReferenceResponse

class ExampleDetailResponse(ExampleBase):
    source: SourceExcerptResponse
