from collections.abc import AsyncIterator

import httpx2
import pytest

from uptime_platform.api_keys.in_memory_repository import (
    InMemoryApiKeyRepository,
)
from uptime_platform.api_keys.repository_dependencies import (
    get_api_key_repository,
)
from uptime_platform.auth.dependencies import (
    get_organization_context,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.main import app

pytestmark = pytest.mark.anyio


@pytest.fixture
def repository() -> InMemoryApiKeyRepository:
    return InMemoryApiKeyRepository()


@pytest.fixture
async def client(
    repository: InMemoryApiKeyRepository,
    organization_context: OrganizationContext,
) -> AsyncIterator[httpx2.AsyncClient]:
    app.dependency_overrides[get_organization_context] = lambda: organization_context

    app.dependency_overrides[get_api_key_repository] = lambda: repository

    transport = httpx2.ASGITransport(
        app=app,
    )

    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


async def test_create_api_key_returns_plaintext_once(
    client: httpx2.AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/api-keys",
        json={
            "name": "CI",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "CI"
    assert data["key"].startswith("upt_")
    assert data["key_prefix"] == data["key"][:12]

    assert "key_hash" not in data


async def test_list_api_keys_does_not_return_plaintext(
    client: httpx2.AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/api-keys",
        json={
            "name": "CI",
        },
    )

    assert create_response.status_code == 201

    response = await client.get("/api/v1/api-keys")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "CI"
    assert "key" not in data[0]
    assert "key_hash" not in data[0]


async def test_delete_api_key(
    client: httpx2.AsyncClient,
) -> None:
    create_response = await client.post(
        "/api/v1/api-keys",
        json={
            "name": "CI",
        },
    )

    assert create_response.status_code == 201

    api_key_id = create_response.json()["id"]

    response = await client.delete(f"/api/v1/api-keys/{api_key_id}")

    assert response.status_code == 204

    response = await client.get(f"/api/v1/api-keys/{api_key_id}")

    assert response.status_code == 404
