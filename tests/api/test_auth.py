import pytest
from fastapi.testclient import TestClient

from uptime_platform.auth.dependencies import (
    get_membership_repository,
    get_organization_repository,
    get_user_repository,
)
from uptime_platform.main import app
from uptime_platform.organizations.in_memory_repository import (
    InMemoryMembershipRepository,
    InMemoryOrganizationRepository,
)
from uptime_platform.users.in_memory_repository import (
    InMemoryUserRepository,
)


@pytest.fixture
def user_repository() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def organization_repository() -> InMemoryOrganizationRepository:
    return InMemoryOrganizationRepository()


@pytest.fixture
def membership_repository() -> InMemoryMembershipRepository:
    return InMemoryMembershipRepository()


@pytest.fixture
def client(
    user_repository: InMemoryUserRepository,
    organization_repository: InMemoryOrganizationRepository,
    membership_repository: InMemoryMembershipRepository,
) -> TestClient:
    app.dependency_overrides[get_user_repository] = lambda: user_repository

    app.dependency_overrides[get_organization_repository] = lambda: (
        organization_repository
    )

    app.dependency_overrides[get_membership_repository] = lambda: membership_repository

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_register(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "strong-password",
            "organization_name": "Acme",
        },
    )

    assert response.status_code == 201

    body = response.json()

    assert body["email"] == "user@example.com"
    assert body["organization_name"] == "Acme"
    assert body["role"] == "owner"

    assert "user_id" in body
    assert "organization_id" in body
    assert "password" not in body
    assert "password_hash" not in body


def test_duplicate_email_returns_conflict(
    client: TestClient,
) -> None:
    payload = {
        "email": "user@example.com",
        "password": "strong-password",
        "organization_name": "Acme",
    }

    first_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert first_response.status_code == 201

    second_response = client.post(
        "/api/v1/auth/register",
        json=payload,
    )

    assert second_response.status_code == 409

    assert second_response.json() == {
        "detail": "Email is already registered",
    }


def test_invalid_registration_returns_422(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "not-an-email",
            "password": "short",
            "organization_name": "",
        },
    )

    assert response.status_code == 422


def register_user(
    client: TestClient,
) -> None:
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "strong-password",
            "organization_name": "Acme",
        },
    )

    assert response.status_code == 201


def test_login_returns_access_token(
    client: TestClient,
) -> None:
    register_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "strong-password",
        },
    )

    assert response.status_code == 200

    body = response.json()

    assert body["token_type"] == "bearer"
    assert isinstance(
        body["access_token"],
        str,
    )
    assert body["access_token"]


def test_login_with_invalid_password_returns_401(
    client: TestClient,
) -> None:
    register_user(client)

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401

    assert response.json() == {
        "detail": "Invalid email or password",
    }


def test_me_returns_authenticated_user(
    client: TestClient,
) -> None:
    register_user(client)

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "strong-password",
        },
    )

    token = login_response.json()["access_token"]

    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    assert response.json()["email"] == ("user@example.com")


def test_me_without_token_returns_401(
    client: TestClient,
) -> None:
    response = client.get("/api/v1/auth/me")

    assert response.status_code == 401


def test_me_with_invalid_token_returns_401(
    client: TestClient,
) -> None:
    response = client.get(
        "/api/v1/auth/me",
        headers={
            "Authorization": ("Bearer invalid-token"),
        },
    )

    assert response.status_code == 401
