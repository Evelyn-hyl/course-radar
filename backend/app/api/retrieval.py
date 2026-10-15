from typing import Annotated

from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.services.retrieval import RetrievalService, get_retrieval_service
from app.schemas.retrieval import RetrievalResponse

router = APIRouter(
    prefix="/courses/{course_id}/search",
    tags=["retrieval"],
)

@router.get("", response_model=RetrievalResponse, status_code=status.HTTP_200_OK)
async def search_chunks(
    course_id: UUID,
    query: str,
    service: Annotated[RetrievalService, Depends(get_retrieval_service)],
    limit: int = 5,
) -> RetrievalResponse:
    return await service.search(
        course_id=course_id,
        query=query,
        limit=limit,
    )