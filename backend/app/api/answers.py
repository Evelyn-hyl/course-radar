from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.answer_generation.client import AnswerGenerationError
from app.embeddings.client import EmbeddingGenerationError
from app.schemas.answers import AnswerRequest, AnswerResponse
from app.services.answers import (
    AnswerCourseNotFoundError,
    AnswerService,
    get_answer_service,
)


router = APIRouter(prefix="/courses/{course_id}/ask", tags=["answers"])


@router.post("", response_model=AnswerResponse)
async def answer_question(
    course_id: UUID,
    request: AnswerRequest,
    service: Annotated[AnswerService, Depends(get_answer_service)],
) -> AnswerResponse:
    try:
        return await service.answer(
            course_id=course_id,
            question=request.question,
        )
    except AnswerCourseNotFoundError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except (EmbeddingGenerationError, AnswerGenerationError) as error:
        raise HTTPException(status_code=502, detail=str(error)) from error
