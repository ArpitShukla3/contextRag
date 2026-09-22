"""Tests for the application startup behaviour."""

from fastapi import FastAPI


def test_create_app_returns_fastapi_instance(app: FastAPI) -> None:
    assert isinstance(app, FastAPI)


def test_app_registers_api_health_route(app: FastAPI) -> None:
    schema = app.openapi()
    assert "/api/health" in schema["paths"]


def test_app_lifespan_starts_and_responds(client) -> None:
    response = client.get("/api/health")
    assert response.status_code == 200