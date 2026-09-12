import pytest
from fastapi.testclient import TestClient

from uptime_platform.auth.config import (
    AuthSettings,
    get_auth_settings,
)
from uptime_platform.auth.dependencies import (
    get_membership_repository,
    get_organization_repository,
    get_user_repository,
)
from uptime_platform.auth.in_memory_refresh_repository import (
    InMemoryRefreshSessionRepository,
)
from uptime_platform.auth.refresh_dependencies import (
    get_refresh_session_repository,
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
def refresh_repository() -> InMemoryRefreshSessionRepository:
    return InMemoryRefreshSessionRepository()


@pytest.fixture
def client(
    user_repository: InMemoryUserRepository,
    organization_repository: InMemoryOrganizationRepository,
    membership_repository: InMemoryMembershipRepository,
    refresh_repository: InMemoryRefreshSessionRepository,
    auth_settings: AuthSettings,
) -> TestClient:
    app.dependency_overrides[get_user_repository] = lambda: user_repository

    app.dependency_overrides[get_organization_repository] = lambda: (
        organization_repository
    )

    app.dependency_overrides[get_membership_repository] = lambda: membership_repository

    app.dependency_overrides[get_refresh_session_repository] = lambda: (
        refresh_repository
    )

    app.dependency_overrides[get_auth_settings] = lambda: auth_settings

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


def test_login_returns_access_token_and_refresh_cookie(
    client: TestClient,
    auth_settings: AuthSettings,
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
    assert body["access_token"]

    refresh_token = response.cookies.get(auth_settings.refresh_cookie_name)

    assert refresh_token is not None
    assert refresh_token.startswith("upr_")

    assert "HttpOnly" in response.headers["set-cookie"]

    assert response.headers["cache-control"] == "no-store"


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


def test_refresh_rotates_refresh_cookie(
    client: TestClient,
    auth_settings: AuthSettings,
) -> None:
    register_user(client)

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "strong-password",
        },
    )

    old_refresh = login_response.cookies.get(auth_settings.refresh_cookie_name)

    assert old_refresh is not None

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 200
    assert response.json()["access_token"]

    new_refresh = response.cookies.get(auth_settings.refresh_cookie_name)

    assert new_refresh is not None
    assert new_refresh != old_refresh


def test_old_refresh_token_cannot_be_reused(
    client: TestClient,
    auth_settings: AuthSettings,
) -> None:
    register_user(client)

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "strong-password",
        },
    )

    old_refresh = login_response.cookies.get(auth_settings.refresh_cookie_name)

    assert old_refresh is not None

    first_refresh = client.post("/api/v1/auth/refresh")

    assert first_refresh.status_code == 200

    client.cookies.clear()

    client.cookies.set(
        auth_settings.refresh_cookie_name,
        old_refresh,
        path="/api/v1/auth",
    )

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401


def test_logout_revokes_refresh_token(
    client: TestClient,
    auth_settings: AuthSettings,
) -> None:
    register_user(client)

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "user@example.com",
            "password": "strong-password",
        },
    )

    refresh_token = login_response.cookies.get(auth_settings.refresh_cookie_name)

    assert refresh_token is not None

    response = client.post("/api/v1/auth/logout")

    assert response.status_code == 204

    client.cookies.clear()

    client.cookies.set(
        auth_settings.refresh_cookie_name,
        refresh_token,
        path="/api/v1/auth",
    )

    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401


def test_refresh_without_cookie_returns_401(
    client: TestClient,
) -> None:
    response = client.post("/api/v1/auth/refresh")

    assert response.status_code == 401
