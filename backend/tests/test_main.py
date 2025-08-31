# Trivial test file update for demo purposes
import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_multiply_basic():
    resp = client.post("/multiply", json={"a": 3, "b": 4})
    assert resp.status_code == 200
    assert resp.json()["result"] == 12

def test_multiply_zero():
    resp = client.post("/multiply", json={"a": 0, "b": 5})
    assert resp.status_code == 200
    assert resp.json()["result"] == 0

def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"
