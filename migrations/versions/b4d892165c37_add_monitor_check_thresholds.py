"""add monitor check thresholds

Revision ID: b4d892165c37
Revises: 365f24dc8803
Create Date: 2026-08-31 16:16:08.228602

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b4d892165c37"
down_revision: str | Sequence[str] | None = "365f24dc8803"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "monitors",
        sa.Column(
            "failure_threshold",
            sa.Integer(),
            server_default="3",
            nullable=False,
        ),
    )

    op.add_column(
        "monitors",
        sa.Column(
            "recovery_threshold",
            sa.Integer(),
            server_default="2",
            nullable=False,
        ),
    )

    op.add_column(
        "monitors",
        sa.Column(
            "consecutive_failures",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )

    op.add_column(
        "monitors",
        sa.Column(
            "consecutive_successes",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column(
        "monitors",
        "consecutive_successes",
    )

    op.drop_column(
        "monitors",
        "consecutive_failures",
    )

    op.drop_column(
        "monitors",
        "recovery_threshold",
    )

    op.drop_column(
        "monitors",
        "failure_threshold",
    )
