from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from uptime_platform.core.config import get_settings

settings = get_settings()

engine = create_async_engine(settings.database_url)

SessionFactory = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    async with SessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
