from datetime import (
    UTC,
    datetime,
    timedelta,
)
from uuid import UUID, uuid4

from uptime_platform.auth.entities import (
    RefreshSession,
    TokenPair,
)
from uptime_platform.auth.exceptions import (
    InvalidRefreshTokenError,
)
from uptime_platform.auth.refresh_protocols import (
    RefreshSessionRepositoryProtocol,
)
from uptime_platform.auth.refresh_security import (
    generate_refresh_token,
    hash_refresh_token,
)
from uptime_platform.auth.token_service import (
    TokenService,
)


class RefreshSessionService:
    def __init__(
        self,
        repository: RefreshSessionRepositoryProtocol,
        token_service: TokenService,
        hash_secret: str,
        ttl_days: int,
    ) -> None:
        self._repository = repository
        self._token_service = token_service
        self._hash_secret = hash_secret
        self._ttl_days = ttl_days

    async def issue(
        self,
        user_id: UUID,
    ) -> TokenPair:
        return await self._create_pair(
            user_id=user_id,
            now=datetime.now(UTC),
        )

    async def refresh(
        self,
        refresh_token: str,
    ) -> TokenPair:
        now = datetime.now(UTC)

        token_hash = hash_refresh_token(
            refresh_token,
            self._hash_secret,
        )

        session = await self._repository.get_by_hash_for_update(token_hash)

        if session is None:
            raise InvalidRefreshTokenError

        if session.revoked_at is not None:
            raise InvalidRefreshTokenError

        if session.expires_at <= now:
            raise InvalidRefreshTokenError

        revoked = await self._repository.revoke(
            session.id,
            now,
        )

        if not revoked:
            raise InvalidRefreshTokenError

        return await self._create_pair(
            user_id=session.user_id,
            now=now,
        )

    async def revoke(
        self,
        refresh_token: str,
    ) -> None:
        token_hash = hash_refresh_token(
            refresh_token,
            self._hash_secret,
        )

        session = await self._repository.get_by_hash_for_update(token_hash)

        if session is None:
            return

        if session.revoked_at is not None:
            return

        await self._repository.revoke(
            session.id,
            datetime.now(UTC),
        )

    async def _create_pair(
        self,
        user_id: UUID,
        now: datetime,
    ) -> TokenPair:
        plaintext_refresh_token = generate_refresh_token()

        session = RefreshSession(
            id=uuid4(),
            user_id=user_id,
            token_hash=hash_refresh_token(
                plaintext_refresh_token,
                self._hash_secret,
            ),
            created_at=now,
            expires_at=(now + timedelta(days=self._ttl_days)),
        )

        await self._repository.create(session)

        access_token = self._token_service.create_access_token(user_id)

        return TokenPair(
            access_token=access_token,
            refresh_token=(plaintext_refresh_token),
        )
