"""API and parsing tests for the TaskMind backend.

These tests use FastAPI's TestClient with an in-memory SQLite database and
never call the Groq API: GROQ_API_KEY is removed for each test, so the
keyword-based fallback parser is used.
"""
import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from BackEnd import backend  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    backend.Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)

    def override_get_db():
        db = TestingSession()
        try:
            yield db
        finally:
            db.close()

    backend.app.dependency_overrides[backend.get_db] = override_get_db
    try:
        with TestClient(backend.app) as test_client:
            yield test_client
    finally:
        backend.app.dependency_overrides.clear()
        engine.dispose()


def test_list_tasks_is_empty_initially(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_create_task_uses_fallback_parser(client):
    response = client.post("/task", json={"original_text": "Buy milk tomorrow, urgent"})
    assert response.status_code == 200

    task = response.json()
    assert task["id"] == 1
    assert task["original_text"] == "Buy milk tomorrow, urgent"
    assert task["priority"] == "High"
    assert task["category"] == "Shopping"
    assert task["deadline"] == "Tomorrow"
    assert task["created_at"] is not None


def test_created_tasks_are_listed(client):
    client.post("/task", json={"original_text": "Finish the report by friday"})
    client.post("/task", json={"original_text": "Maybe read a book later"})

    response = client.get("/tasks")
    assert response.status_code == 200
    tasks = response.json()
    assert [t["id"] for t in tasks] == [1, 2]
    assert tasks[0]["category"] == "Work"
    assert tasks[0]["deadline"] == "This week"
    assert tasks[1]["priority"] == "Low"


def test_create_task_requires_original_text(client):
    response = client.post("/task", json={})
    assert response.status_code == 422


def test_fallback_parsing_defaults():
    result = backend.fallback_parsing("Call the plumber")
    assert result["priority"] == "Medium"
    assert result["category"] == "General"
    assert result["deadline"] == "No deadline"
    assert result["notes"] == ""


def test_fallback_parsing_truncates_long_titles():
    text = "a" * 60
    result = backend.fallback_parsing(text)
    assert len(result["title"]) == 50
    assert result["title"].endswith("...")


def test_reform_with_llm_falls_back_without_api_key(monkeypatch):
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    result = backend.reform_with_llm("Go to the gym today")
    assert result["category"] == "Personal"
    assert result["deadline"] == "Today"
