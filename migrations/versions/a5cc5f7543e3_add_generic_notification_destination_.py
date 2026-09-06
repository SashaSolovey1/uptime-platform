"""add generic notification destination config

Revision ID: a5cc5f7543e3
Revises: 4741c9f0a468
Create Date: 2026-09-06 15:05:51.977873
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a5cc5f7543e3"
down_revision: str | Sequence[str] | None = "4741c9f0a468"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute(
        """
        ALTER TYPE notification_destination_type
        ADD VALUE IF NOT EXISTS 'telegram'
        """
    )

    op.add_column(
        "notification_destinations",
        sa.Column(
            "config",
            postgresql.JSONB(
                astext_type=sa.Text(),
            ),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE notification_destinations
        SET config = jsonb_build_object(
            'url', webhook_url,
            'secret', webhook_secret
        )
        WHERE destination_type = 'webhook'
        """
    )

    op.alter_column(
        "notification_destinations",
        "config",
        nullable=False,
    )

    op.drop_column(
        "notification_destinations",
        "webhook_url",
    )

    op.drop_column(
        "notification_destinations",
        "webhook_secret",
    )


def downgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM notification_destinations
                WHERE destination_type <> 'webhook'
            ) THEN
                RAISE EXCEPTION
                    'Cannot downgrade while non-webhook '
                    'notification destinations exist';
            END IF;
        END
        $$;
        """
    )

    op.add_column(
        "notification_destinations",
        sa.Column(
            "webhook_url",
            sa.String(length=2048),
            nullable=True,
        ),
    )

    op.add_column(
        "notification_destinations",
        sa.Column(
            "webhook_secret",
            sa.Text(),
            nullable=True,
        ),
    )

    op.execute(
        """
        UPDATE notification_destinations
        SET
            webhook_url = config ->> 'url',
            webhook_secret = config ->> 'secret'
        WHERE destination_type = 'webhook'
        """
    )

    op.alter_column(
        "notification_destinations",
        "webhook_url",
        nullable=False,
    )

    op.alter_column(
        "notification_destinations",
        "webhook_secret",
        nullable=False,
    )

    op.drop_column(
        "notification_destinations",
        "config",
    )

    op.execute(
        """
        ALTER TABLE notification_destinations
        ALTER COLUMN destination_type TYPE text
        USING destination_type::text
        """
    )

    op.execute(
        """
        DROP TYPE notification_destination_type
        """
    )

    op.execute(
        """
        CREATE TYPE notification_destination_type
        AS ENUM ('webhook')
        """
    )

    op.execute(
        """
        ALTER TABLE notification_destinations
        ALTER COLUMN destination_type
        TYPE notification_destination_type
        USING destination_type::notification_destination_type
        """
    )
