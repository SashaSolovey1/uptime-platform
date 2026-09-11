from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.api_keys.entities import ApiKey
from uptime_platform.api_keys.models import ApiKeyModel


class SqlAlchemyApiKeyRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        api_key: ApiKey,
    ) -> ApiKey:
        model = ApiKeyModel(
            id=api_key.id,
            organization_id=api_key.organization_id,
            name=api_key.name,
            key_hash=api_key.key_hash,
            key_prefix=api_key.key_prefix,
            created_at=api_key.created_at,
            last_used_at=api_key.last_used_at,
        )

        self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(
        self,
        api_key_id: UUID,
        organization_id: UUID,
    ) -> ApiKey | None:
        statement = select(ApiKeyModel).where(
            ApiKeyModel.id == api_key_id,
            ApiKeyModel.organization_id == organization_id,
        )

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_hash(
        self,
        key_hash: str,
    ) -> ApiKey | None:
        statement = select(ApiKeyModel).where(ApiKeyModel.key_hash == key_hash)

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    async def get_all(
        self,
        organization_id: UUID,
    ) -> list[ApiKey]:
        statement = (
            select(ApiKeyModel)
            .where(ApiKeyModel.organization_id == organization_id)
            .order_by(ApiKeyModel.created_at)
        )

        result = await self._session.execute(statement)

        return [self._to_entity(model) for model in result.scalars().all()]

    async def delete(
        self,
        api_key_id: UUID,
        organization_id: UUID,
    ) -> bool:
        statement = select(ApiKeyModel).where(
            ApiKeyModel.id == api_key_id,
            ApiKeyModel.organization_id == organization_id,
        )

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return False

        await self._session.delete(model)
        await self._session.flush()

        return True

    async def update_last_used(
        self,
        api_key_id: UUID,
        last_used_at: datetime,
    ) -> bool:
        statement = (
            update(ApiKeyModel)
            .where(ApiKeyModel.id == api_key_id)
            .values(last_used_at=last_used_at)
            .returning(ApiKeyModel.id)
        )

        result = await self._session.execute(statement)

        updated_id = result.scalar_one_or_none()

        return updated_id is not None

    @staticmethod
    def _to_entity(
        model: ApiKeyModel,
    ) -> ApiKey:
        return ApiKey(
            id=model.id,
            organization_id=model.organization_id,
            name=model.name,
            key_hash=model.key_hash,
            key_prefix=model.key_prefix,
            created_at=model.created_at,
            last_used_at=model.last_used_at,
        )
