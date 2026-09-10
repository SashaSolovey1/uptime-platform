import pytest
from fastapi.testclient import TestClient

from uptime_platform.main import app
from uptime_platform.monitors.dependencies import (
    get_monitor_repository,
)
from uptime_platform.monitors.in_memory_repository import (
    InMemoryMonitorRepository,
)


@pytest.fixture
def repository() -> InMemoryMonitorRepository:
    return InMemoryMonitorRepository()


@pytest.fixture
def client(
    repository: InMemoryMonitorRepository,
) -> TestClient:
    app.dependency_overrides[get_monitor_repository] = lambda: repository

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_create_monitor(client: TestClient) -> None:
    response = client.post(
        "/api/v1/monitors",
        json={
            "name": "Production API",
            "monitor_type": "http",
            "config": {
                "url": "https://example.com/health",
            },
            "interval_seconds": 30,
            "timeout_seconds": 5,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Production API"
    assert data["monitor_type"] == "http"

    assert data["config"] == {
        "url": "https://example.com/health",
        "method": "GET",
        "expected_status_codes": None,
        "body_contains": None,
        "follow_redirects": False,
        "verify_tls": True,
    }

    assert data["interval_seconds"] == 30
    assert data["timeout_seconds"] == 5
    assert data["status"] == "pending"
    assert "id" in data
    assert "created_at" in data


def test_get_monitor(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/monitors",
        json={
            "name": "Production API",
            "monitor_type": "http",
            "config": {
                "url": "https://example.com/health",
            },
        },
    )

    monitor_id = create_response.json()["id"]

    response = client.get(f"/api/v1/monitors/{monitor_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == monitor_id
    assert data["name"] == "Production API"


def test_get_nonexistent_monitor_returns_404(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/monitors/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
    assert response.json() == {
        "detail": "Monitor not found",
    }


def test_create_monitor_with_invalid_data_returns_422(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/monitors",
        json={
            "name": "",
            "url": "not-a-url",
            "interval_seconds": 2,
        },
    )

    assert response.status_code == 422


def test_delete_monitor(client: TestClient) -> None:
    create_response = client.post(
        "/api/v1/monitors",
        json={
            "name": "Production API",
            "monitor_type": "http",
            "config": {
                "url": "https://example.com/health",
            },
        },
    )

    monitor_id = create_response.json()["id"]

    delete_response = client.delete(f"/api/v1/monitors/{monitor_id}")

    assert delete_response.status_code == 204

    get_response = client.get(f"/api/v1/monitors/{monitor_id}")

    assert get_response.status_code == 404


def test_update_monitor(
    client: TestClient,
) -> None:
    create_response = client.post(
        "/api/v1/monitors",
        json={
            "name": "Production API",
            "monitor_type": "http",
            "config": {
                "url": "https://example.com/health",
            },
            "interval_seconds": 30,
            "timeout_seconds": 5,
        },
    )

    monitor_id = create_response.json()["id"]

    response = client.patch(
        f"/api/v1/monitors/{monitor_id}",
        json={
            "timeout_seconds": 15,
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["id"] == monitor_id
    assert body["name"] == "Production API"
    assert body["interval_seconds"] == 30
    assert body["timeout_seconds"] == 15
