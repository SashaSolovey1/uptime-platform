from dataclasses import replace
from datetime import datetime
from uuid import UUID

from uptime_platform.auth.entities import (
    RefreshSession,
)


class InMemoryRefreshSessionRepository:
    def __init__(self) -> None:
        self._sessions: dict[
            UUID,
            RefreshSession,
        ] = {}

    async def create(
        self,
        session: RefreshSession,
    ) -> RefreshSession:
        self._sessions[session.id] = session

        return session

    async def get_by_hash_for_update(
        self,
        token_hash: str,
    ) -> RefreshSession | None:
        for session in self._sessions.values():
            if session.token_hash == token_hash:
                return session

        return None

    async def revoke(
        self,
        session_id: UUID,
        revoked_at: datetime,
    ) -> bool:
        session = self._sessions.get(session_id)

        if session is None:
            return False

        if session.revoked_at is not None:
            return False

        self._sessions[session_id] = replace(
            session,
            revoked_at=revoked_at,
        )

        return True
