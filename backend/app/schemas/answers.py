from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class AnswerRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2_000)

    @field_validator("question")
    @classmethod
    def normalize_question(cls, question: str) -> str:
        normalized = question.strip()
        if not normalized:
            raise ValueError("Question cannot be blank.")
        return normalized


class AnswerCitation(BaseModel):
    chunk_id: UUID
    document_id: UUID
    document_title: str
    page_start: int
    page_end: int


class AnswerResponse(BaseModel):
    answer: str
    citations: list[AnswerCitation]
