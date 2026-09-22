"""Tests for the health endpoint."""


def test_health_returns_ok(client) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_health_response_schema(client) -> None:
    response = client.get("/api/health")
    body = response.json()

    assert set(body.keys()) == {"status"}
    assert isinstance(body["status"], str)