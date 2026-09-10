"""add dns monitor type

Revision ID: 852cc32ed855
Revises: ce47d3285727
Create Date: 2026-09-08 20:35:36.711640

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "852cc32ed855"
down_revision: str | Sequence[str] | None = "ce47d3285727"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE monitor_type ADD VALUE IF NOT EXISTS 'dns'")


def downgrade() -> None:
    bind = op.get_bind()

    dns_monitor_count = bind.execute(
        sa.text(
            """
            SELECT count(*)
            FROM monitors
            WHERE monitor_type = 'dns'
            """
        )
    ).scalar_one()

    if dns_monitor_count > 0:
        raise RuntimeError("Cannot downgrade while DNS monitors exist")

    op.execute("ALTER TYPE monitor_type RENAME TO monitor_type_old")

    op.execute(
        """
        CREATE TYPE monitor_type
        AS ENUM ('http', 'tcp')
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
