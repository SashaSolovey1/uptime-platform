from collections.abc import AsyncIterator

import httpx2
import pytest

from uptime_platform.main import app
from uptime_platform.notifications.destination_dependencies import (
    get_notification_destination_repository,
)
from uptime_platform.notifications.in_memory_repository import (
    InMemoryNotificationDestinationRepository,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository() -> InMemoryNotificationDestinationRepository:
    return InMemoryNotificationDestinationRepository()


@pytest.fixture
async def client(
    repository: InMemoryNotificationDestinationRepository,
) -> AsyncIterator[httpx2.AsyncClient]:
    def override_repository() -> InMemoryNotificationDestinationRepository:
        return repository

    app.dependency_overrides[get_notification_destination_repository] = (
        override_repository
    )

    transport = httpx2.ASGITransport(app=app)

    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


async def test_create_notification_destination(
    client: httpx2.AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/notification-destinations",
        json={
            "name": "Production webhook",
            "destination_type": "webhook",
            "enabled": True,
            "config": {
                "url": "https://example.com/webhook",
                "secret": "very-secret-key-123",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Production webhook"
    assert data["destination_type"] == "webhook"
    assert data["enabled"] is True

    assert data["config"]["url"] == "https://example.com/webhook"
    assert "secret" not in data["config"]


async def test_list_notification_destinations(
    client: httpx2.AsyncClient,
) -> None:
    await client.post(
        "/api/v1/notification-destinations",
        json={
            "name": "Production webhook",
            "destination_type": "webhook",
            "config": {
                "url": "https://example.com/webhook",
                "secret": "very-secret-key-123",
            },
        },
    )

    response = await client.get("/api/v1/notification-destinations")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Production webhook"
    assert data[0]["config"]["url"] == "https://example.com/webhook"
    assert "secret" not in data[0]["config"]


async def test_update_notification_destination(
    client: httpx2.AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/notification-destinations",
        json={
            "name": "Production webhook",
            "destination_type": "webhook",
            "config": {
                "url": "https://example.com/webhook",
                "secret": "very-secret-key-123",
            },
        },
    )

    destination_id = create_response.json()["id"]

    response = await client.patch(
        (f"/api/v1/notification-destinations/{destination_id}"),
        json={
            "name": "Updated webhook",
            "enabled": False,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Updated webhook"
    assert data["enabled"] is False


async def test_delete_notification_destination(
    client: httpx2.AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/notification-destinations",
        json={
            "name": "Production webhook",
            "destination_type": "webhook",
            "config": {
                "url": "https://example.com/webhook",
                "secret": "very-secret-key-123",
            },
        },
    )

    destination_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/v1/notification-destinations/{destination_id}"
    )

    assert response.status_code == 204

    response = await client.get(f"/api/v1/notification-destinations/{destination_id}")

    assert response.status_code == 404


async def test_create_telegram_destination(
    client: httpx2.AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/notification-destinations",
        json={
            "name": "Production Telegram",
            "destination_type": "telegram",
            "enabled": True,
            "config": {
                "bot_token": ("123456789:test-bot-token"),
                "chat_id": "-1001234567890",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Production Telegram"
    assert data["destination_type"] == "telegram"
    assert data["enabled"] is True

    assert data["config"]["chat_id"] == "-1001234567890"

    assert "bot_token" not in data["config"]
