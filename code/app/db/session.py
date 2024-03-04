from sqlalchemy import NullPool, create_engine
from sqlalchemy.orm import sessionmaker

from core.config import DATABASE_URI


engine = create_engine(
    DATABASE_URI,
    echo=False,
    future=True,
    poolclass=NullPool
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
