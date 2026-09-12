from datetime import (
    UTC,
    datetime,
    timedelta,
)
from uuid import uuid4

import pytest

from uptime_platform.auth.entities import (
    RefreshSession,
)
from uptime_platform.auth.exceptions import (
    InvalidRefreshTokenError,
)
from uptime_platform.auth.in_memory_refresh_repository import (
    InMemoryRefreshSessionRepository,
)
from uptime_platform.auth.refresh_security import (
    hash_refresh_token,
)
from uptime_platform.auth.refresh_service import (
    RefreshSessionService,
)
from uptime_platform.auth.token_service import (
    TokenService,
)

pytestmark = pytest.mark.anyio


TEST_JWT_SECRET = "0123456789abcdef0123456789abcdef"

TEST_REFRESH_SECRET = "test-refresh-token-hash-secret-0123456789abcdef"


def make_service() -> tuple[
    RefreshSessionService,
    InMemoryRefreshSessionRepository,
    TokenService,
]:
    repository = InMemoryRefreshSessionRepository()

    token_service = TokenService(
        secret=TEST_JWT_SECRET,
        algorithm="HS256",
        access_token_ttl_minutes=60,
    )

    service = RefreshSessionService(
        repository=repository,
        token_service=token_service,
        hash_secret=TEST_REFRESH_SECRET,
        ttl_days=30,
    )

    return (
        service,
        repository,
        token_service,
    )


async def test_issue_creates_refresh_session() -> None:
    (
        service,
        repository,
        token_service,
    ) = make_service()

    user_id = uuid4()

    pair = await service.issue(user_id)

    assert token_service.get_user_id(pair.access_token) == user_id

    assert pair.refresh_token.startswith("upr_")

    session = await repository.get_by_hash_for_update(
        hash_refresh_token(
            pair.refresh_token,
            TEST_REFRESH_SECRET,
        )
    )

    assert session is not None
    assert session.user_id == user_id
    assert session.revoked_at is None


async def test_refresh_rotates_token() -> None:
    service, repository, _ = make_service()

    first = await service.issue(uuid4())

    second = await service.refresh(first.refresh_token)

    assert second.refresh_token != first.refresh_token

    old_session = await repository.get_by_hash_for_update(
        hash_refresh_token(
            first.refresh_token,
            TEST_REFRESH_SECRET,
        )
    )

    assert old_session is not None
    assert old_session.revoked_at is not None

    with pytest.raises(InvalidRefreshTokenError):
        await service.refresh(first.refresh_token)


async def test_expired_refresh_token_is_rejected() -> None:
    service, repository, _ = make_service()

    plaintext = "upr_expired-test-token"
    now = datetime.now(UTC)

    await repository.create(
        RefreshSession(
            id=uuid4(),
            user_id=uuid4(),
            token_hash=hash_refresh_token(
                plaintext,
                TEST_REFRESH_SECRET,
            ),
            created_at=(now - timedelta(days=31)),
            expires_at=(now - timedelta(seconds=1)),
        )
    )

    with pytest.raises(InvalidRefreshTokenError):
        await service.refresh(plaintext)


async def test_revoked_refresh_token_is_rejected() -> None:
    service, _, _ = make_service()

    pair = await service.issue(uuid4())

    await service.revoke(pair.refresh_token)

    with pytest.raises(InvalidRefreshTokenError):
        await service.refresh(pair.refresh_token)
