"""Test wiring/access-control của REST routes — không seed DB đầy đủ (xem db/seed.py
cho kiểm thử thủ công end-to-end qua docker compose)."""
from fastapi.testclient import TestClient

from gateway.app.main import app

client = TestClient(app)


def test_health_still_ok_after_new_routers():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_teacher_dashboard_requires_auth():
    response = client.get("/teacher/dashboard/1")
    assert response.status_code == 401


def test_parent_dashboard_requires_auth():
    response = client.get("/parent/dashboard/1")
    assert response.status_code == 401


def test_diagnostic_submit_answer_requires_auth():
    response = client.post(
        "/diagnostic/submit-answer", json={"question_id": 1, "student_answer": "x"}
    )
    assert response.status_code == 401


def test_practice_path_requires_auth():
    response = client.get("/practice/path")
    assert response.status_code == 401
