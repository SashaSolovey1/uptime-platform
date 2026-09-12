from datetime import UTC, datetime
from uuid import uuid4

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials

from uptime_platform.api_keys.config import (
    ApiKeySettings,
)
from uptime_platform.api_keys.in_memory_repository import (
    InMemoryApiKeyRepository,
)
from uptime_platform.auth.dependencies import (
    get_organization_context,
    require_admin,
    require_member,
    require_owner,
)
from uptime_platform.auth.entities import (
    OrganizationContext,
)
from uptime_platform.auth.token_service import (
    TokenService,
)
from uptime_platform.organizations.entities import (
    Membership,
    Organization,
    OrganizationRole,
)
from uptime_platform.organizations.in_memory_repository import (
    InMemoryMembershipRepository,
    InMemoryOrganizationRepository,
)
from uptime_platform.users.entities import User
from uptime_platform.users.in_memory_repository import (
    InMemoryUserRepository,
)

pytestmark = pytest.mark.anyio


TEST_JWT_SECRET = "0123456789abcdef0123456789abcdef"

TEST_API_KEY_HASH_SECRET = "test-api-key-hash-secret-0123456789abcdef"


def make_user() -> User:
    return User(
        id=uuid4(),
        email="user@example.com",
        password_hash="not-used",
        created_at=datetime.now(UTC),
    )


def make_context(
    role: OrganizationRole,
) -> OrganizationContext:
    now = datetime.now(UTC)

    user = make_user()

    organization = Organization(
        id=uuid4(),
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


def make_token_service() -> TokenService:
    return TokenService(
        secret=TEST_JWT_SECRET,
        algorithm="HS256",
        access_token_ttl_minutes=60,
    )


def make_api_key_settings() -> ApiKeySettings:
    return ApiKeySettings(
        api_key_hash_secret=TEST_API_KEY_HASH_SECRET,
    )


@pytest.mark.parametrize(
    "role",
    [
        OrganizationRole.MEMBER,
        OrganizationRole.ADMIN,
        OrganizationRole.OWNER,
    ],
)
async def test_member_permission_accepts_member_and_above(
    role: OrganizationRole,
) -> None:
    context = make_context(role)

    result = await require_member(context)

    assert result == context


async def test_member_permission_rejects_viewer() -> None:
    context = make_context(OrganizationRole.VIEWER)

    with pytest.raises(HTTPException) as exc_info:
        await require_member(context)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient permissions"


@pytest.mark.parametrize(
    "role",
    [
        OrganizationRole.ADMIN,
        OrganizationRole.OWNER,
    ],
)
async def test_admin_permission_accepts_admin_and_owner(
    role: OrganizationRole,
) -> None:
    context = make_context(role)

    result = await require_admin(context)

    assert result == context


@pytest.mark.parametrize(
    "role",
    [
        OrganizationRole.VIEWER,
        OrganizationRole.MEMBER,
    ],
)
async def test_admin_permission_rejects_lower_roles(
    role: OrganizationRole,
) -> None:
    context = make_context(role)

    with pytest.raises(HTTPException) as exc_info:
        await require_admin(context)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient permissions"


async def test_owner_permission_accepts_owner() -> None:
    context = make_context(OrganizationRole.OWNER)

    result = await require_owner(context)

    assert result == context


@pytest.mark.parametrize(
    "role",
    [
        OrganizationRole.VIEWER,
        OrganizationRole.MEMBER,
        OrganizationRole.ADMIN,
    ],
)
async def test_owner_permission_rejects_non_owner(
    role: OrganizationRole,
) -> None:
    context = make_context(role)

    with pytest.raises(HTTPException) as exc_info:
        await require_owner(context)

    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Insufficient permissions"


async def test_organization_context_rejects_user_without_membership() -> None:
    organization_repository = InMemoryOrganizationRepository()

    membership_repository = InMemoryMembershipRepository()

    user_repository = InMemoryUserRepository()
    api_key_repository = InMemoryApiKeyRepository()

    user = make_user()

    organization = Organization(
        id=uuid4(),
        name="Secret Organization",
        created_at=datetime.now(UTC),
    )

    await user_repository.create(user)

    await organization_repository.create(organization)

    token_service = make_token_service()

    token = token_service.create_access_token(user.id)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    with pytest.raises(HTTPException) as exc_info:
        await get_organization_context(
            credentials=credentials,
            token_service=token_service,
            user_repository=user_repository,
            organization_repository=organization_repository,
            membership_repository=membership_repository,
            api_key_repository=api_key_repository,
            api_key_settings=make_api_key_settings(),
            organization_id=organization.id,
        )

    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Organization not found"


async def test_organization_context_returns_membership() -> None:
    organization_repository = InMemoryOrganizationRepository()

    membership_repository = InMemoryMembershipRepository()

    user_repository = InMemoryUserRepository()
    api_key_repository = InMemoryApiKeyRepository()

    user = make_user()

    organization = Organization(
        id=uuid4(),
        name="Test Organization",
        created_at=datetime.now(UTC),
    )

    membership = Membership(
        id=uuid4(),
        organization_id=organization.id,
        user_id=user.id,
        role=OrganizationRole.ADMIN,
        created_at=datetime.now(UTC),
    )

    await user_repository.create(user)

    await organization_repository.create(organization)

    await membership_repository.create(membership)

    token_service = make_token_service()

    token = token_service.create_access_token(user.id)

    credentials = HTTPAuthorizationCredentials(
        scheme="Bearer",
        credentials=token,
    )

    result = await get_organization_context(
        credentials=credentials,
        token_service=token_service,
        user_repository=user_repository,
        organization_repository=organization_repository,
        membership_repository=membership_repository,
        api_key_repository=api_key_repository,
        api_key_settings=make_api_key_settings(),
        organization_id=organization.id,
    )

    assert result.user == user
    assert result.organization == organization
    assert result.membership == membership
    assert result.api_key is None
    assert result.role is OrganizationRole.ADMIN
