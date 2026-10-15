from unittest import IsolatedAsyncioTestCase
from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app
from app.schemas.answers import AnswerResponse
from app.services.answers import get_answer_service


class _FakeAnswerService:
    def __init__(self) -> None:
        self.question: str | None = None

    async def answer(self, *, course_id: object, question: str) -> AnswerResponse:
        self.question = question
        return AnswerResponse(answer="A grounded answer.", citations=[])


class AnswerApiTests(IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.service = _FakeAnswerService()
        app.dependency_overrides[get_answer_service] = lambda: self.service
        self.client = TestClient(app)

    def tearDown(self) -> None:
        app.dependency_overrides.clear()

    async def test_answers_a_course_question(self) -> None:
        response = self.client.post(
            f"/courses/{uuid4()}/ask",
            json={"question": "  What is Dirac's theorem?  "},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"answer": "A grounded answer.", "citations": []},
        )
        self.assertEqual(self.service.question, "What is Dirac's theorem?")

    async def test_rejects_a_blank_question(self) -> None:
        response = self.client.post(
            f"/courses/{uuid4()}/ask",
            json={"question": "   "},
        )

        self.assertEqual(response.status_code, 422)
