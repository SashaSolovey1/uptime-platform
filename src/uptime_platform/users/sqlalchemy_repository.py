from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.users.entities import User
from uptime_platform.users.models import UserModel


class SqlAlchemyUserRepository:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self._session = session

    async def create(
        self,
        user: User,
    ) -> User:
        model = UserModel(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            created_at=user.created_at,
        )

        self._session.add(model)

        await self._session.flush()
        await self._session.refresh(model)

        return self._to_entity(model)

    async def get_by_id(
        self,
        user_id: UUID,
    ) -> User | None:
        model = await self._session.get(
            UserModel,
            user_id,
        )

        if model is None:
            return None

        return self._to_entity(model)

    async def get_by_email(
        self,
        email: str,
    ) -> User | None:
        statement = select(UserModel).where(UserModel.email == email)

        result = await self._session.execute(statement)

        model = result.scalar_one_or_none()

        if model is None:
            return None

        return self._to_entity(model)

    @staticmethod
    def _to_entity(
        model: UserModel,
    ) -> User:
        return User(
            id=model.id,
            email=model.email,
            password_hash=model.password_hash,
            created_at=model.created_at,
        )
