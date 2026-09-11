from collections.abc import AsyncIterator
from datetime import UTC, datetime

import httpx2
import pytest

from uptime_platform.api_keys.in_memory_repository import (
    InMemoryApiKeyRepository,
)
from uptime_platform.api_keys.repository_dependencies import (
    get_api_key_repository,
)
from uptime_platform.api_keys.schemas import (
    ApiKeyCreate,
)
from uptime_platform.api_keys.service import (
    ApiKeyService,
)
from uptime_platform.auth.dependencies import (
    get_organization_repository,
)
from uptime_platform.main import app
from uptime_platform.monitors.dependencies import (
    get_monitor_repository,
)
from uptime_platform.monitors.in_memory_repository import (
    InMemoryMonitorRepository,
)
from uptime_platform.organizations.entities import (
    Organization,
)
from uptime_platform.organizations.in_memory_repository import (
    InMemoryOrganizationRepository,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def api_key_repository() -> InMemoryApiKeyRepository:
    return InMemoryApiKeyRepository()


@pytest.fixture
def organization_repository() -> InMemoryOrganizationRepository:
    return InMemoryOrganizationRepository()


@pytest.fixture
def monitor_repository() -> InMemoryMonitorRepository:
    return InMemoryMonitorRepository()


@pytest.fixture
async def api_key(
    api_key_repository: InMemoryApiKeyRepository,
    organization_repository: InMemoryOrganizationRepository,
) -> str:
    organization = Organization(
        id=__import__("uuid").uuid4(),
        name="API Key Organization",
        created_at=datetime.now(UTC),
    )

    await organization_repository.create(organization)

    service = ApiKeyService(
        repository=api_key_repository,
        organization_id=organization.id,
    )

    result = await service.create(
        ApiKeyCreate(
            name="CI",
        )
    )

    return result.plaintext_key


@pytest.fixture
async def client(
    api_key_repository: InMemoryApiKeyRepository,
    organization_repository: InMemoryOrganizationRepository,
    monitor_repository: InMemoryMonitorRepository,
) -> AsyncIterator[httpx2.AsyncClient]:
    app.dependency_overrides[get_api_key_repository] = lambda: api_key_repository

    app.dependency_overrides[get_organization_repository] = lambda: (
        organization_repository
    )

    app.dependency_overrides[get_monitor_repository] = lambda: monitor_repository

    transport = httpx2.ASGITransport(
        app=app,
    )

    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


async def test_api_key_can_read_monitors(
    client: httpx2.AsyncClient,
    api_key: str,
) -> None:
    response = await client.get(
        "/api/v1/monitors",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
    )

    assert response.status_code == 200
    assert response.json() == []


async def test_api_key_can_create_monitor(
    client: httpx2.AsyncClient,
    api_key: str,
) -> None:
    response = await client.post(
        "/api/v1/monitors",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "name": "Production API",
            "monitor_type": "http",
            "config": {
                "url": "https://example.com/health",
            },
        },
    )

    assert response.status_code == 201

    assert response.json()["name"] == "Production API"


async def test_api_key_cannot_manage_status_pages(
    client: httpx2.AsyncClient,
    api_key: str,
) -> None:
    response = await client.post(
        "/api/v1/status-pages",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
        json={
            "name": "Production",
            "slug": "production",
        },
    )

    assert response.status_code == 403


async def test_invalid_api_key_is_rejected(
    client: httpx2.AsyncClient,
) -> None:
    response = await client.get(
        "/api/v1/monitors",
        headers={
            "Authorization": ("Bearer upt_this-key-does-not-exist"),
        },
    )

    assert response.status_code == 401


async def test_api_key_updates_last_used_at(
    client: httpx2.AsyncClient,
    api_key: str,
    api_key_repository: InMemoryApiKeyRepository,
) -> None:
    from uptime_platform.api_keys.security import (
        hash_api_key,
    )

    stored = await api_key_repository.get_by_hash(hash_api_key(api_key))

    assert stored is not None
    assert stored.last_used_at is None

    response = await client.get(
        "/api/v1/monitors",
        headers={
            "Authorization": f"Bearer {api_key}",
        },
    )

    assert response.status_code == 200

    stored = await api_key_repository.get_by_hash(hash_api_key(api_key))

    assert stored is not None
    assert stored.last_used_at is not None
