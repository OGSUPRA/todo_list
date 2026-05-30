from __future__ import annotations

import os
import sys
from collections.abc import Generator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

os.environ["SECRET_KEY"] = "test-secret-key-with-at-least-32-characters"
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["MEDIA_ROOT"] = str(Path(__file__).parent / "media")
Path(os.environ["MEDIA_ROOT"]).mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.api.deps import get_db_session
from app.main import app
from app.models import Base
from app.core.config import settings

engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def override_get_db_session() -> Generator[Session, None, None]:
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


app.dependency_overrides[get_db_session] = override_get_db_session


@pytest.fixture(autouse=True)
def reset_state(tmp_path: Path) -> Generator[None, None, None]:
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    media_root = tmp_path / "media"
    media_root.mkdir(parents=True, exist_ok=True)
    settings.media_root = str(media_root)

    yield


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    user_payload = {
        "username": "tester",
        "email": "tester@example.com",
        "password": "strong-password",
    }
    client.post("/api/v1/auth/register", json=user_payload)
    response = client.post(
        "/api/v1/auth/login",
        json={"username": user_payload["username"], "password": user_payload["password"]},
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
