import os

os.environ["DATABASE_URL"] = "sqlite:////tmp/acervo_hub_tests.sqlite3"
os.environ["SECRET_KEY"] = "test-secret"
os.environ["SEED_DATABASE"] = "false"
os.environ["PASSWORD_HASH_ROUNDS"] = "4"

import pytest
from sqlalchemy import select

from app.database.session import Base, SessionLocal, engine
from app.models import User
from app.services.seed import seed_database


@pytest.fixture()
def db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = SessionLocal()
    seed_database(session)
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def admin(db):
    return db.scalar(select(User).where(User.email == "admin@example.com"))


@pytest.fixture()
def reader(db):
    return db.scalar(select(User).where(User.email == "leitor@example.com"))
