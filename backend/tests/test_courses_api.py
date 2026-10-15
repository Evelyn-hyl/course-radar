from uuid import UUID, uuid4
from unittest import TestCase

from fastapi.testclient import TestClient

from app.db.models import Course
from app.main import app
from app.schemas.courses import CourseCreate
from app.services.courses import get_course_service


class _FakeCourseService:
    def __init__(self) -> None:
        self.course_id = uuid4()
        self.received: CourseCreate | None = None

    def create(self, course_data: CourseCreate) -> Course:
        self.received = course_data
        return Course(id=self.course_id, name=course_data.name)


class CourseApiTests(TestCase):
    def setUp(self) -> None:
        self.service = _FakeCourseService()
        app.dependency_overrides[get_course_service] = lambda: self.service
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    def test_creates_a_course_and_normalizes_its_name(self) -> None:
        response = self.client.post(
            "/courses",
            json={"name": "  MATH   180A  "},
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.json(),
            {"id": str(self.service.course_id), "name": "MATH 180A"},
        )
        self.assertEqual(self.service.received, CourseCreate(name="MATH 180A"))

    def test_rejects_a_blank_course_name(self) -> None:
        response = self.client.post("/courses", json={"name": "   "})

        self.assertEqual(response.status_code, 422)

    def test_returns_a_uuid(self) -> None:
        response = self.client.post("/courses", json={"name": "MATH 180A"})

        UUID(response.json()["id"])
