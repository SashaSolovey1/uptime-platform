from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    select,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.auth.entities import (
    RefreshSession,
)
from uptime_platform.auth.models import (
    RefreshSessionModel,
)


class SqlAlchemyRefreshSessionRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        session: RefreshSession,
    ) -> RefreshSession:
        model = RefreshSessionModel(
            id=session.id,
            user_id=session.user_id,
            token_hash=session.token_hash,
            created_at=session.created_at,
            expires_at=session.expires_at,
            revoked_at=session.revoked_at,
        )

        self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_hash_for_update(
        self,
        token_hash: str,
    ) -> RefreshSession | None:
        statement = (
            select(RefreshSessionModel)
            .where(RefreshSessionModel.token_hash == token_hash)
            .with_for_update()
            .execution_options(populate_existing=True)
        )

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def revoke(
        self,
        session_id: UUID,
        revoked_at: datetime,
    ) -> bool:
        statement = (
            update(RefreshSessionModel)
            .where(
                RefreshSessionModel.id == session_id,
                RefreshSessionModel.revoked_at.is_(None),
            )
            .values(revoked_at=revoked_at)
            .returning(RefreshSessionModel.id)
        )

        result = await self._session.execute(statement)

        return result.scalar_one_or_none() is not None

    @staticmethod
    def _to_entity(
        model: RefreshSessionModel,
    ) -> RefreshSession:
        return RefreshSession(
            id=model.id,
            user_id=model.user_id,
            token_hash=model.token_hash,
            created_at=model.created_at,
            expires_at=model.expires_at,
            revoked_at=model.revoked_at,
        )
