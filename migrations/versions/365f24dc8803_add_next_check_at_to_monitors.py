"""add next check at to monitors

Revision ID: 365f24dc8803
Revises: 93ef03022add
Create Date: 2026-08-31 15:20:12.056565

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "365f24dc8803"
down_revision: str | Sequence[str] | None = "93ef03022add"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "monitors",
        sa.Column(
            "next_check_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE monitors
        SET next_check_at = NOW()
        WHERE next_check_at IS NULL
        """
    )

    op.alter_column(
        "monitors",
        "next_check_at",
        nullable=False,
    )

    op.create_index(
        "ix_monitors_next_check_at",
        "monitors",
        ["next_check_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_monitors_next_check_at",
        table_name="monitors",
    )

    op.drop_column(
        "monitors",
        "next_check_at",
    )
