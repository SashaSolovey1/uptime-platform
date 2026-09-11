from collections.abc import AsyncIterator
from datetime import UTC, datetime
from uuid import UUID, uuid4

import httpx2
import pytest

from uptime_platform.auth.dependencies import (
    get_organization_context,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.main import app
from uptime_platform.monitors.dependencies import (
    get_monitor_repository,
)
from uptime_platform.monitors.in_memory_repository import (
    InMemoryMonitorRepository,
)
from uptime_platform.notifications.destination_dependencies import (
    get_notification_destination_repository,
)
from uptime_platform.notifications.in_memory_repository import (
    InMemoryNotificationDestinationRepository,
)
from uptime_platform.organizations.entities import (
    Membership,
    Organization,
    OrganizationRole,
)
from uptime_platform.status_pages.dependencies import (
    get_status_page_service,
)
from uptime_platform.status_pages.in_memory_repository import (
    InMemoryStatusPageRepository,
)
from uptime_platform.status_pages.service import (
    StatusPageService,
)
from uptime_platform.users.entities import User

pytestmark = pytest.mark.anyio


ORGANIZATION_ID = UUID("11111111-1111-1111-1111-111111111111")


def make_context(
    role: OrganizationRole,
) -> OrganizationContext:
    now = datetime.now(UTC)

    user = User(
        id=uuid4(),
        email=f"{role.value}@example.com",
        password_hash="not-used",
        created_at=now,
    )

    organization = Organization(
        id=ORGANIZATION_ID,
        name="Test Organization",
        created_at=now,
    )

    membership = Membership(
        id=uuid4(),
        organization_id=organization.id,
        user_id=user.id,
        role=role,
        created_at=now,
    )

    return OrganizationContext(
        user=user,
        organization=organization,
        membership=membership,
    )


def use_role(
    role: OrganizationRole,
) -> None:
    context = make_context(role)

    app.dependency_overrides[get_organization_context] = lambda: context


@pytest.fixture
def monitor_repository() -> InMemoryMonitorRepository:
    return InMemoryMonitorRepository()


@pytest.fixture
def status_page_repository() -> InMemoryStatusPageRepository:
    return InMemoryStatusPageRepository()


@pytest.fixture
def notification_repository() -> InMemoryNotificationDestinationRepository:
    return InMemoryNotificationDestinationRepository()


@pytest.fixture
async def client(
    monitor_repository: InMemoryMonitorRepository,
    status_page_repository: InMemoryStatusPageRepository,
    notification_repository: InMemoryNotificationDestinationRepository,
) -> AsyncIterator[httpx2.AsyncClient]:
    app.dependency_overrides[get_monitor_repository] = lambda: monitor_repository

    def override_status_page_service() -> StatusPageService:
        return StatusPageService(
            repository=status_page_repository,
            monitor_repository=monitor_repository,
            organization_id=ORGANIZATION_ID,
        )

    app.dependency_overrides[get_status_page_service] = override_status_page_service

    app.dependency_overrides[get_notification_destination_repository] = lambda: (
        notification_repository
    )

    transport = httpx2.ASGITransport(
        app=app,
    )

    async with httpx2.AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as async_client:
        yield async_client

    app.dependency_overrides.clear()


async def test_viewer_can_read_monitors(
    client: httpx2.AsyncClient,
) -> None:
    use_role(OrganizationRole.VIEWER)

    response = await client.get("/api/v1/monitors")

    assert response.status_code == 200
    assert response.json() == []


async def test_viewer_cannot_create_monitor(
    client: httpx2.AsyncClient,
) -> None:
    use_role(OrganizationRole.VIEWER)

    response = await client.post(
        "/api/v1/monitors",
        json={
            "name": "Production API",
            "monitor_type": "http",
            "config": {
                "url": "https://example.com/health",
            },
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}


async def test_member_can_create_monitor(
    client: httpx2.AsyncClient,
) -> None:
    use_role(OrganizationRole.MEMBER)

    response = await client.post(
        "/api/v1/monitors",
        json={
            "name": "Production API",
            "monitor_type": "http",
            "config": {
                "url": "https://example.com/health",
            },
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Production API"


async def test_member_cannot_create_status_page(
    client: httpx2.AsyncClient,
) -> None:
    use_role(OrganizationRole.MEMBER)

    response = await client.post(
        "/api/v1/status-pages",
        json={
            "name": "Production",
            "slug": "production",
        },
    )

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}


async def test_admin_can_create_status_page(
    client: httpx2.AsyncClient,
) -> None:
    use_role(OrganizationRole.ADMIN)

    response = await client.post(
        "/api/v1/status-pages",
        json={
            "name": "Production",
            "slug": "production",
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Production"
    assert data["slug"] == "production"


async def test_member_cannot_create_notification_destination(
    client: httpx2.AsyncClient,
) -> None:
    use_role(OrganizationRole.MEMBER)

    response = await client.post(
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

    assert response.status_code == 403
    assert response.json() == {"detail": "Insufficient permissions"}


async def test_admin_can_create_notification_destination(
    client: httpx2.AsyncClient,
) -> None:
    use_role(OrganizationRole.ADMIN)

    response = await client.post(
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

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Production webhook"
    assert data["destination_type"] == "webhook"


async def test_owner_can_use_admin_endpoint(
    client: httpx2.AsyncClient,
) -> None:
    use_role(OrganizationRole.OWNER)

    response = await client.post(
        "/api/v1/status-pages",
        json={
            "name": "Owner Status",
            "slug": "owner-status",
        },
    )

    assert response.status_code == 201
