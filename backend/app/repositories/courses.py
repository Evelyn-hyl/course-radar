from sqlalchemy.orm import Session

from app.db.models import Course


class CourseRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def add(self, course: Course) -> None:
        self._session.add(course)
