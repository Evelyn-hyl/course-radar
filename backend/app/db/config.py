import os
from pathlib import Path

from dotenv import load_dotenv


DATABASE_URL_ENVIRONMENT_VARIABLE = "DATABASE_URL"
BACKEND_DIRECTORY = Path(__file__).resolve().parents[2]


def load_backend_environment() -> None:
    load_dotenv(BACKEND_DIRECTORY / ".env")


def get_database_url() -> str:
    """Return the SQLAlchemy database URL from the process environment."""
    load_backend_environment()
    database_url = os.getenv(DATABASE_URL_ENVIRONMENT_VARIABLE)
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Expected a SQLAlchemy PostgreSQL URL, "
            "for example postgresql+psycopg2://user:password@localhost/course_radar."
        )
    return database_url
