from datetime import UTC, datetime, timedelta

import pytest
from pydantic import ValidationError

from uptime_platform.statistics.schemas import (
    StatisticsPeriod,
    StatisticsQuery,
)


def test_period_is_valid() -> None:
    query = StatisticsQuery(period=StatisticsPeriod.DAYS_7)

    assert query.period is StatisticsPeriod.DAYS_7


def test_custom_range_is_valid() -> None:
    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(days=5)

    query = StatisticsQuery(
        starts_at=starts_at,
        ends_at=ends_at,
    )

    assert query.starts_at == starts_at
    assert query.ends_at == ends_at


def test_period_and_custom_range_cannot_be_combined() -> None:
    starts_at = datetime.now(UTC)
    ends_at = starts_at + timedelta(days=1)

    with pytest.raises(ValidationError):
        StatisticsQuery(
            period=StatisticsPeriod.DAYS_7,
            starts_at=starts_at,
            ends_at=ends_at,
        )


def test_custom_range_requires_both_dates() -> None:
    with pytest.raises(ValidationError):
        StatisticsQuery(starts_at=datetime.now(UTC))


def test_ends_at_must_be_after_starts_at() -> None:
    starts_at = datetime.now(UTC)

    with pytest.raises(ValidationError):
        StatisticsQuery(
            starts_at=starts_at,
            ends_at=starts_at - timedelta(hours=1),
        )


def test_custom_range_cannot_exceed_90_days() -> None:
    starts_at = datetime.now(UTC)

    with pytest.raises(ValidationError):
        StatisticsQuery(
            starts_at=starts_at,
            ends_at=starts_at + timedelta(days=91),
        )


def test_custom_range_requires_timezone() -> None:
    starts_at = datetime(  # noqa: DTZ001
        2026,
        9,
        1,
    )

    ends_at = datetime(  # noqa: DTZ001
        2026,
        9,
        2,
    )

    with pytest.raises(ValidationError):
        StatisticsQuery(
            starts_at=starts_at,
            ends_at=ends_at,
        )
