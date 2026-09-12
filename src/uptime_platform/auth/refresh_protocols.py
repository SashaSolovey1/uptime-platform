from datetime import datetime
from typing import Protocol
from uuid import UUID

from uptime_platform.auth.entities import (
    RefreshSession,
)


class RefreshSessionRepositoryProtocol(Protocol):
    async def create(
        self,
        session: RefreshSession,
    ) -> RefreshSession: ...

    async def get_by_hash_for_update(
        self,
        token_hash: str,
    ) -> RefreshSession | None: ...

    async def revoke(
        self,
        session_id: UUID,
        revoked_at: datetime,
    ) -> bool: ...
