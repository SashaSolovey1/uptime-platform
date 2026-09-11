from datetime import UTC, datetime
from uuid import uuid4

import pytest
from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from uptime_platform.organizations.constants import DEFAULT_ORGANIZATION_ID
from uptime_platform.outbox.entities import (
    OutboxEvent,
    OutboxEventType,
)
from uptime_platform.outbox.models import OutboxEventModel
from uptime_platform.outbox.sqlalchemy_repository import (
    SqlAlchemyOutboxRepository,
)

pytestmark = pytest.mark.anyio
from collections.abc import AsyncIterator


@pytest.fixture(autouse=True)
async def clean_outbox(
    session_factory: async_sessionmaker[AsyncSession],
) -> AsyncIterator[None]:
    async with session_factory() as session:
        await session.execute(delete(OutboxEventModel))
        await session.commit()

    yield

    async with session_factory() as session:
        await session.execute(delete(OutboxEventModel))
        await session.commit()


def make_event() -> OutboxEvent:
    return OutboxEvent(
        id=uuid4(),
        organization_id=DEFAULT_ORGANIZATION_ID,
        event_type=OutboxEventType.INCIDENT_OPENED,
        payload={
            "incident_id": str(uuid4()),
            "monitor_id": str(uuid4()),
        },
        created_at=datetime.now(UTC),
        processed_at=None,
    )


async def test_claim_pending_skips_event_locked_by_another_transaction(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    event = make_event()

    async with session_factory() as setup_session, setup_session.begin():
        repository = SqlAlchemyOutboxRepository(setup_session)

        await repository.create(event)

    async with (
        session_factory() as session_1,
        session_factory() as session_2,
        session_1.begin(),
    ):
        repository_1 = SqlAlchemyOutboxRepository(session_1)

        claimed_by_worker_1 = await repository_1.claim_pending(limit=1)

        assert len(claimed_by_worker_1) == 1
        assert claimed_by_worker_1[0].id == event.id

        async with session_2.begin():
            repository_2 = SqlAlchemyOutboxRepository(session_2)

            claimed_by_worker_2 = await repository_2.claim_pending(limit=1)

            assert claimed_by_worker_2 == []


async def test_claim_pending_allows_workers_to_claim_different_events(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    event_1 = make_event()
    event_2 = make_event()

    async with session_factory() as setup_session, setup_session.begin():
        repository = SqlAlchemyOutboxRepository(setup_session)

        await repository.create(event_1)

        await repository.create(event_2)

    async with (
        session_factory() as session_1,
        session_factory() as session_2,
        session_1.begin(),
    ):
        repository_1 = SqlAlchemyOutboxRepository(session_1)

        claimed_by_worker_1 = await repository_1.claim_pending(limit=1)

        assert len(claimed_by_worker_1) == 1

        async with session_2.begin():
            repository_2 = SqlAlchemyOutboxRepository(session_2)

            claimed_by_worker_2 = await repository_2.claim_pending(limit=1)

            assert len(claimed_by_worker_2) == 1

            assert claimed_by_worker_1[0].id != claimed_by_worker_2[0].id


async def test_claimed_event_becomes_available_after_transaction_ends(
    session_factory: async_sessionmaker[AsyncSession],
) -> None:
    event = make_event()

    async with session_factory() as setup_session, setup_session.begin():
        repository = SqlAlchemyOutboxRepository(setup_session)

        await repository.create(event)

    async with session_factory() as session_1, session_1.begin():
        repository = SqlAlchemyOutboxRepository(session_1)

        claimed = await repository.claim_pending(limit=1)

        assert len(claimed) == 1

    # transaction 1 уже закончилась, lock снят

    async with session_factory() as session_2, session_2.begin():
        repository = SqlAlchemyOutboxRepository(session_2)

        claimed = await repository.claim_pending(limit=1)

        assert len(claimed) == 1
        assert claimed[0].id == event.id
