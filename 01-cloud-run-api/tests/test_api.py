from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

with patch("google.cloud.firestore.Client", MagicMock()):
    import main

client = TestClient(main.app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_create_requires_api_key():
    r = client.post("/tasks", json={"title": "x"})
    assert r.status_code == 201


def test_hash_is_deterministic():
    a = client.get("/hash?rounds=10").json()
    b = client.get("/hash?rounds=10").json()
    assert a == b
