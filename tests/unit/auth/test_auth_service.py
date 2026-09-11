from datetime import UTC, datetime

import pytest

from uptime_platform.auth.exceptions import (
    EmailAlreadyRegisteredError,
    InvalidCredentialsError,
)
from uptime_platform.auth.schemas import (
    LoginRequest,
    RegisterRequest,
)
from uptime_platform.auth.security import (
    verify_password,
)
from uptime_platform.auth.service import AuthService
from uptime_platform.organizations.constants import (
    DEFAULT_ORGANIZATION_ID,
)
from uptime_platform.organizations.entities import (
    Organization,
    OrganizationRole,
)
from uptime_platform.organizations.in_memory_repository import (
    InMemoryMembershipRepository,
    InMemoryOrganizationRepository,
)
from uptime_platform.users.in_memory_repository import (
    InMemoryUserRepository,
)

pytestmark = pytest.mark.anyio


def make_service() -> tuple[
    AuthService,
    InMemoryUserRepository,
    InMemoryOrganizationRepository,
    InMemoryMembershipRepository,
]:
    user_repository = InMemoryUserRepository()
    organization_repository = InMemoryOrganizationRepository()
    membership_repository = InMemoryMembershipRepository()

    service = AuthService(
        user_repository=user_repository,
        organization_repository=organization_repository,
        membership_repository=membership_repository,
    )

    return (
        service,
        user_repository,
        organization_repository,
        membership_repository,
    )


async def test_register_creates_user_and_owner_membership() -> None:
    (
        service,
        user_repository,
        _,
        membership_repository,
    ) = make_service()

    result = await service.register(
        RegisterRequest(
            email="USER@example.com",
            password="strong-password",
            organization_name="Acme",
        )
    )

    assert result.user.email == "user@example.com"

    assert result.user.password_hash != "strong-password"

    assert verify_password(
        "strong-password",
        result.user.password_hash,
    )

    stored_user = await user_repository.get_by_id(result.user.id)

    assert stored_user == result.user

    membership = await membership_repository.get_by_user_and_organization(
        user_id=result.user.id,
        organization_id=result.organization.id,
    )

    assert membership is not None
    assert membership.role is OrganizationRole.OWNER


async def test_first_user_claims_default_organization() -> None:
    (
        service,
        _,
        organization_repository,
        _,
    ) = make_service()

    default_organization = Organization(
        id=DEFAULT_ORGANIZATION_ID,
        name="Default Organization",
        created_at=datetime.now(UTC),
    )

    await organization_repository.create(default_organization)

    result = await service.register(
        RegisterRequest(
            email="owner@example.com",
            password="strong-password",
            organization_name="My Company",
        )
    )

    assert result.organization.id == DEFAULT_ORGANIZATION_ID

    assert result.organization.name == "My Company"


async def test_second_user_gets_new_organization() -> None:
    (
        service,
        _,
        organization_repository,
        _,
    ) = make_service()

    await organization_repository.create(
        Organization(
            id=DEFAULT_ORGANIZATION_ID,
            name="Default Organization",
            created_at=datetime.now(UTC),
        )
    )

    first = await service.register(
        RegisterRequest(
            email="first@example.com",
            password="strong-password",
            organization_name="First Company",
        )
    )

    second = await service.register(
        RegisterRequest(
            email="second@example.com",
            password="strong-password",
            organization_name="Second Company",
        )
    )

    assert first.organization.id == DEFAULT_ORGANIZATION_ID

    assert second.organization.id != DEFAULT_ORGANIZATION_ID

    assert first.organization.id != second.organization.id


async def test_duplicate_email_is_rejected() -> None:
    service, _, _, _ = make_service()

    data = RegisterRequest(
        email="user@example.com",
        password="strong-password",
        organization_name="Acme",
    )

    await service.register(data)

    with pytest.raises(EmailAlreadyRegisteredError):
        await service.register(data)


async def test_login_returns_user_for_valid_credentials() -> None:
    service, _, _, _ = make_service()

    registered = await service.register(
        RegisterRequest(
            email="user@example.com",
            password="strong-password",
            organization_name="Acme",
        )
    )

    user = await service.login(
        LoginRequest(
            email="USER@example.com",
            password="strong-password",
        )
    )

    assert user == registered.user


async def test_login_rejects_invalid_password() -> None:
    service, _, _, _ = make_service()

    await service.register(
        RegisterRequest(
            email="user@example.com",
            password="strong-password",
            organization_name="Acme",
        )
    )

    with pytest.raises(InvalidCredentialsError):
        await service.login(
            LoginRequest(
                email="user@example.com",
                password="wrong-password",
            )
        )


async def test_login_rejects_unknown_email() -> None:
    service, _, _, _ = make_service()

    with pytest.raises(InvalidCredentialsError):
        await service.login(
            LoginRequest(
                email="unknown@example.com",
                password="strong-password",
            )
        )
