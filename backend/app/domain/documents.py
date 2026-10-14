from enum import StrEnum

class SourceType(StrEnum):
    TEXTBOOK = "textbook"
    LECTURE_SLIDES = "lecture_slides"
    LECTURE_TRANSCRIPT = "lecture_transcript"
    LECTURE_SUMMARY = "lecture_summary"
    HOMEWORK = "homework"
    QUIZ = "quiz"

class DocumentStatus(StrEnum):
    PENDING = "pending"
    PROCESSING = "processing"
    READY = "ready"
    FAILED = "failed"

class ConceptType(StrEnum):
    DEFINITION = "definition"
    THEOREM = "theorem"
    PROPOSITION = "proposition"
    LEMMA = "lemma"
    EQUATION = "equation"
    COROLLARY = "corollary"

# For ingestion
class ChunkContentType(StrEnum):
    DEFINITION = "definition"
    THEOREM = "theorem"
    PROPOSITION = "proposition"
    LEMMA = "lemma"
    EQUATION = "equation"
    EXAMPLE = "example"
    PROOF = "proof"
    OTHER = "other"

class ExampleConceptRelationship(StrEnum):
    DIRECT_APPLICATION = "direct_application"
    BACKGROUND = "background"
    UNRELATED = "unrelated"
    UNKNOWN = "unknown"


class VerificationStatus(StrEnum):
    EXPLICIT_REFERENCE = "explicit_reference"
    MODEL_INFERRED = "model_inferred"
    HUMAN_VERIFIED = "human_verified"

class ExtractionStatus(StrEnum):
    SUCCESS = "success"
    PARTIAL = "partial"
    FAILED = "failed"