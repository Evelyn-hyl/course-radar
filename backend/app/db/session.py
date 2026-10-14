from collections.abc import Iterator
from functools import lru_cache

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.config import get_database_url


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    return create_engine(get_database_url(), pool_pre_ping=True)


def get_session() -> Iterator[Session]:
    """Provide one SQLAlchemy session and always close it after use."""
    
    session_factory = sessionmaker(bind=get_engine())
    with session_factory() as session:
        yield session
