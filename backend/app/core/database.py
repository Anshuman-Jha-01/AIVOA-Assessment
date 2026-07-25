"""
Sets up the SQLAlchemy engine and session factory.

`get_db()` is a FastAPI dependency — every route that needs DB access
declares `db: Session = Depends(get_db)` and FastAPI handles opening/
closing the session automatically, per-request.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.core.config import settings

engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
