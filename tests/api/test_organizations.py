from collections.abc import AsyncIterator

import httpx2
import pytest

from uptime_platform.auth.dependencies import (
    get_current_user,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.main import app
from uptime_platform.organizations.dependencies import (
    get_organization_service,
)
from uptime_platform.organizations.in_memory_repository import (
    InMemoryMembershipRepository,
    InMemoryOrganizationRepository,
)
from uptime_platform.organizations.service import (
    OrganizationService,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
def organization_service() -> OrganizationService:
    return OrganizationService(
        organization_repository=(InMemoryOrganizationRepository()),
        membership_repository=(InMemoryMembershipRepository()),
    )


@pytest.fixture
async def client(
    organization_service: OrganizationService,
    organization_context: OrganizationContext,
) -> AsyncIterator[httpx2.AsyncClient]:
    app.dependency_overrides[get_current_user] = lambda: organization_context.user

    app.dependency_overrides[get_organization_service] = lambda: organization_service

    transport = httpx2.ASGITransport(
        app=app,
    )

    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


async def test_create_organization(
    client: httpx2.AsyncClient,
) -> None:
    response = await client.post(
        "/api/v1/organizations",
        json={
            "name": "Acme",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Acme"
    assert data["role"] == "owner"
    assert data["id"]
    assert data["created_at"]


async def test_list_organizations(
    client: httpx2.AsyncClient,
) -> None:
    first_response = await client.post(
        "/api/v1/organizations",
        json={
            "name": "First",
        },
    )

    second_response = await client.post(
        "/api/v1/organizations",
        json={
            "name": "Second",
        },
    )

    assert first_response.status_code == 201
    assert second_response.status_code == 201

    response = await client.get("/api/v1/organizations")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2

    assert {organization["name"] for organization in data} == {
        "First",
        "Second",
    }

    assert all(organization["role"] == "owner" for organization in data)
