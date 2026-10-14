import os


DATABASE_URL_ENVIRONMENT_VARIABLE = "DATABASE_URL"


def get_database_url() -> str:
    """Return the SQLAlchemy database URL from the process environment."""
    
    database_url = os.getenv(DATABASE_URL_ENVIRONMENT_VARIABLE)
    if not database_url:
        raise RuntimeError(
            "DATABASE_URL is not set. Expected a SQLAlchemy PostgreSQL URL, "
            "for example postgresql+psycopg2://user:password@localhost/course_radar."
        )
    return database_url
