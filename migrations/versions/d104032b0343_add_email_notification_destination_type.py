"""add email notification destination type

Revision ID: d104032b0343
Revises: a5cc5f7543e3
Create Date: 2026-09-06 19:33:16.055011

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d104032b0343"
down_revision: str | Sequence[str] | None = "a5cc5f7543e3"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE notification_destination_type ADD VALUE IF NOT EXISTS 'email'"
    )


def downgrade() -> None:
    raise RuntimeError(
        "Downgrade is not supported because PostgreSQL "
        "cannot safely remove an enum value"
    )
