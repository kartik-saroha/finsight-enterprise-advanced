import os
from pathlib import Path
from fastapi.testclient import TestClient

# The app reads its database URL on import. The test command sets this to a temporary SQLite file.
os.environ.setdefault("DATABASE_URL", "sqlite:///./finsight_test.db")
os.environ.setdefault("JWT_SECRET_KEY", "unit-test-secret-key-with-enough-entropy-123456")
os.environ.setdefault("ALLOW_DEV_SECRET", "1")
from app.main import app

client = TestClient(app)

def user_payload():
    return {"email": "test-user@example.com", "password": "CorrectHorseBattery12!"}

def token_for(email="test-user@example.com"):
    r = client.post("/api/v1/auth/register", json={"email": email, "password": "CorrectHorseBattery12!"})
    if r.status_code == 409:
        r = client.post("/api/v1/auth/login", json={"email": email, "password": "CorrectHorseBattery12!"})
    assert r.status_code in (201, 200), r.text
    return r.json()["access_token"]

def test_health():
    r = client.get("/healthz")
    assert r.status_code == 200 and r.json()["status"] == "ok"

def test_register_rejects_short_password():
    r = client.post("/api/v1/auth/register", json={"email":"short@example.com", "password":"tiny"})
    assert r.status_code == 422

def test_auth_and_user_profile():
    token = token_for("profile-test@example.com")
    r = client.get("/api/v1/me", headers={"Authorization":f"Bearer {token}"})
    assert r.status_code == 200 and r.json()["email"] == "profile-test@example.com"

def test_protected_endpoint_rejects_anonymous():
    assert client.get("/api/v1/obligations").status_code == 401

def test_obligation_crud_is_user_scoped():
    token = token_for("obligations-test@example.com"); headers = {"Authorization":f"Bearer {token}"}
    r = client.post("/api/v1/obligations", headers=headers, json={"name":"Rent", "amount":12000, "due_date":"2026-11-01", "kind":"Rent"})
    assert r.status_code == 201, r.text
    oid = r.json()["id"]
    assert any(x["id"] == oid for x in client.get("/api/v1/obligations", headers=headers).json())
    assert client.patch(f"/api/v1/obligations/{oid}/paid", headers=headers).status_code == 200
    other = token_for("other-user@example.com")
    assert client.patch(f"/api/v1/obligations/{oid}/paid", headers={"Authorization":f"Bearer {other}"}).status_code == 404

def test_ai_fallback_returns_explainable_schema():
    token = token_for("agents-test@example.com")
    r = client.post("/api/v1/agents/orchestrate", headers={"Authorization":f"Bearer {token}"}, json={"question":"Can I cover bills this month?", "financial_context":{"cash":10000,"upcoming_obligations":12000}})
    assert r.status_code == 200, r.text
    data = r.json()
    assert data["fallback_used"] is True
    assert data["provider"] == "rules"
    assert len(data["findings"]) >= 1
    assert "evidence" in data["findings"][0]
