"""enforce single open incident per monitor

Revision ID: b7d86e7389f6
Revises: 12eb624ee878
Create Date: 2026-09-13 14:40:20.417654

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b7d86e7389f6"
down_revision: str | Sequence[str] | None = "12eb624ee878"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            WITH ranked AS (
                SELECT
                    id,
                    ROW_NUMBER() OVER (
                        PARTITION BY monitor_id
                        ORDER BY started_at ASC, id ASC
                    ) AS row_number
                FROM incidents
                WHERE status = 'open'
            )
            UPDATE incidents AS incident
            SET
                status = 'resolved',
                resolved_at = incident.started_at
            FROM ranked
            WHERE incident.id = ranked.id
              AND ranked.row_number > 1
            """
        )
    )

    op.create_index(
        "uq_incidents_one_open_per_monitor",
        "incidents",
        ["monitor_id"],
        unique=True,
        postgresql_where=sa.text("status = 'open'"),
    )


def downgrade() -> None:
    op.drop_index(
        "uq_incidents_one_open_per_monitor",
        table_name="incidents",
    )
