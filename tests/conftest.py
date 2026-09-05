from collections.abc import AsyncIterator

import pytest
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from uptime_platform.checks.models import CheckModel
from uptime_platform.monitors.models import MonitorModel


class TestSettings(BaseSettings):
    database_url: str

    model_config = SettingsConfigDict(
        env_file=".env.test",
        env_file_encoding="utf-8",
    )


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture
async def session_factory() -> AsyncIterator[async_sessionmaker[AsyncSession]]:
    settings = TestSettings()

    engine = create_async_engine(
        settings.database_url,
    )

    factory = async_sessionmaker(
        bind=engine,
        expire_on_commit=False,
    )

    try:
        yield factory

    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[AsyncSession]:
    async with session_factory() as session:
        await session.execute(delete(CheckModel))
        await session.execute(delete(MonitorModel))
        await session.commit()

        try:
            yield session

        finally:
            await session.rollback()

            await session.execute(delete(CheckModel))
            await session.execute(delete(MonitorModel))
            await session.commit()
