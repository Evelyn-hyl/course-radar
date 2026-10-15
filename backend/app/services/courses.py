from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.models import Course
from app.db.session import get_session
from app.repositories.courses import CourseRepository
from app.schemas.courses import CourseCreate


class CourseService:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(self, course_data: CourseCreate) -> Course:
        course = Course(name=course_data.name)
        CourseRepository(self._session).add(course)
        self._session.commit()
        self._session.refresh(course)
        return course


def get_course_service(
    session: Annotated[Session, Depends(get_session)],
) -> CourseService:
    return CourseService(session)
