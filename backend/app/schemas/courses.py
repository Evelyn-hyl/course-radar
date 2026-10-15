from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CourseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)

    @field_validator("name")
    @classmethod
    def normalize_name(cls, name: str) -> str:
        normalized = " ".join(name.split())
        if not normalized:
            raise ValueError("Course name cannot be blank.")
        return normalized


class CourseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
