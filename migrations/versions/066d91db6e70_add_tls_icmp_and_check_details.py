"""add tls icmp and check details

Revision ID: 066d91db6e70
Revises: 852cc32ed855
Create Date: 2026-09-10 13:11:48.994056

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "066d91db6e70"
down_revision: str | Sequence[str] | None = "852cc32ed855"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE monitor_type ADD VALUE IF NOT EXISTS 'tls'")

    op.execute("ALTER TYPE monitor_type ADD VALUE IF NOT EXISTS 'icmp'")

    op.add_column(
        "checks",
        sa.Column(
            "details",
            postgresql.JSONB(),
            nullable=True,
        ),
    )


def downgrade() -> None:
    bind = op.get_bind()

    unsupported_monitor_count = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM monitors
            WHERE monitor_type IN ('tls', 'icmp')
            """
        )
    ).scalar_one()

    if unsupported_monitor_count > 0:
        raise RuntimeError("Cannot downgrade while TLS or ICMP monitors exist")

    op.drop_column(
        "checks",
        "details",
    )

    op.execute("ALTER TYPE monitor_type RENAME TO monitor_type_old")

    op.execute(
        """
        CREATE TYPE monitor_type
        AS ENUM ('http', 'tcp', 'dns')
        """
    )

    op.execute(
        """
        ALTER TABLE monitors
        ALTER COLUMN monitor_type
        TYPE monitor_type
        USING monitor_type::text::monitor_type
        """
    )

    op.execute("DROP TYPE monitor_type_old")
