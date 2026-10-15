from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.schemas.courses import CourseCreate, CourseResponse
from app.services.courses import CourseService, get_course_service


router = APIRouter(prefix="/courses", tags=["courses"])


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
def create_course(
    course_data: CourseCreate,
    service: Annotated[CourseService, Depends(get_course_service)],
) -> CourseResponse:
    return CourseResponse.model_validate(service.create(course_data))
