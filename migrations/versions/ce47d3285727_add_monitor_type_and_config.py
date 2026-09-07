"""add monitor type and config

Revision ID: ce47d3285727
Revises: d104032b0343
Create Date: 2026-09-07 15:39:16.843583

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "ce47d3285727"
down_revision: str | Sequence[str] | None = "d104032b0343"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


monitor_type_enum = postgresql.ENUM(
    "http",
    "tcp",
    name="monitor_type",
)


def upgrade() -> None:
    bind = op.get_bind()

    monitor_type_enum.create(
        bind,
        checkfirst=True,
    )

    op.add_column(
        "monitors",
        sa.Column(
            "monitor_type",
            monitor_type_enum,
            nullable=True,
        ),
    )

    op.add_column(
        "monitors",
        sa.Column(
            "config",
            postgresql.JSONB(),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE monitors
            SET
                monitor_type = 'http',
                config = jsonb_build_object(
                    'url',
                    url
                )
            """
        )
    )

    op.alter_column(
        "monitors",
        "monitor_type",
        nullable=False,
    )

    op.alter_column(
        "monitors",
        "config",
        nullable=False,
    )

    op.drop_column(
        "monitors",
        "url",
    )


def downgrade() -> None:
    bind = op.get_bind()

    tcp_monitor_count = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM monitors
            WHERE monitor_type <> 'http'
            """
        )
    ).scalar_one()

    if tcp_monitor_count > 0:
        raise RuntimeError("Cannot downgrade while non-HTTP monitors exist")

    op.add_column(
        "monitors",
        sa.Column(
            "url",
            sa.String(length=2048),
            nullable=True,
        ),
    )

    op.execute(
        sa.text(
            """
            UPDATE monitors
            SET url = config ->> 'url'
            WHERE monitor_type = 'http'
            """
        )
    )

    op.alter_column(
        "monitors",
        "url",
        nullable=False,
    )

    op.drop_column(
        "monitors",
        "config",
    )

    op.drop_column(
        "monitors",
        "monitor_type",
    )

    monitor_type_enum.drop(
        bind,
        checkfirst=True,
    )
