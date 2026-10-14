from typing import Literal, TypedDict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.documents import router as documents_router


class HealthResponse(TypedDict):
    status: Literal["ok"]


app = FastAPI(title="CourseRadar API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(documents_router)


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return {"status": "ok"}

