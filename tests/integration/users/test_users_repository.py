from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from uptime_platform.users.entities import User
from uptime_platform.users.models import UserModel
from uptime_platform.users.sqlalchemy_repository import (
    SqlAlchemyUserRepository,
)

pytestmark = pytest.mark.anyio


@pytest.fixture
async def repository(
    db_session: AsyncSession,
) -> SqlAlchemyUserRepository:
    await db_session.execute(delete(UserModel))
    await db_session.commit()

    return SqlAlchemyUserRepository(db_session)


def make_user() -> User:
    return User(
        id=uuid4(),
        email=f"{uuid4()}@example.com",
        password_hash="hashed-password",
        created_at=datetime.now(UTC),
    )


async def test_create_user(
    repository: SqlAlchemyUserRepository,
) -> None:
    user = make_user()

    created = await repository.create(user)

    assert created == user


async def test_get_user_by_id(
    repository: SqlAlchemyUserRepository,
) -> None:
    user = make_user()

    await repository.create(user)

    found = await repository.get_by_id(user.id)

    assert found == user


async def test_get_user_by_email(
    repository: SqlAlchemyUserRepository,
) -> None:
    user = make_user()

    await repository.create(user)

    found = await repository.get_by_email(user.email)

    assert found == user


async def test_get_nonexistent_user_returns_none(
    repository: SqlAlchemyUserRepository,
) -> None:
    found = await repository.get_by_id(uuid4())

    assert found is None
