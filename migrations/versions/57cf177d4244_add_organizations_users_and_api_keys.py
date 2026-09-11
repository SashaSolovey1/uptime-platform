"""add organizations users and api keys

Revision ID: 57cf177d4244
Revises: 066d91db6e70
Create Date: 2026-09-10 18:04:08.459699
"""

from collections.abc import Sequence
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "57cf177d4244"
down_revision: str | Sequence[str] | None = "066d91db6e70"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


DEFAULT_ORGANIZATION_ID = UUID("00000000-0000-0000-0000-000000000001")


def _organization_id_bind() -> sa.BindParameter[UUID]:
    return sa.bindparam(
        "organization_id",
        value=DEFAULT_ORGANIZATION_ID,
        type_=sa.Uuid(as_uuid=True),
    )


organization_role_enum = postgresql.ENUM(
    "owner",
    "admin",
    "member",
    "viewer",
    name="organization_role",
)


def upgrade() -> None:
    bind = op.get_bind()

    organization_role_enum.create(
        bind,
        checkfirst=True,
    )

    op.create_table(
        "organizations",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=320),
            nullable=False,
        ),
        sa.Column(
            "password_hash",
            sa.String(length=512),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_users_email",
        "users",
        ["email"],
        unique=True,
    )

    op.create_table(
        "memberships",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "role",
            postgresql.ENUM(
                "owner",
                "admin",
                "member",
                "viewer",
                name="organization_role",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_memberships_organization_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_memberships_user_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "user_id",
            name="uq_membership_organization_user",
        ),
    )

    op.create_index(
        "ix_memberships_organization_id",
        "memberships",
        ["organization_id"],
        unique=False,
    )

    op.create_index(
        "ix_memberships_user_id",
        "memberships",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "api_keys",
        sa.Column(
            "id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.Uuid(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "key_hash",
            sa.String(length=64),
            nullable=False,
        ),
        sa.Column(
            "key_prefix",
            sa.String(length=32),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
        ),
        sa.Column(
            "last_used_at",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_api_keys_organization_id",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "key_hash",
            name="uq_api_keys_key_hash",
        ),
    )

    op.create_index(
        "ix_api_keys_key_prefix",
        "api_keys",
        ["key_prefix"],
        unique=False,
    )

    op.create_index(
        "ix_api_keys_organization_id",
        "api_keys",
        ["organization_id"],
        unique=False,
    )

    # Existing installations may already have monitors, notification
    # destinations, status pages and outbox events. Create one organization
    # that will own all legacy resources.
    op.execute(
        sa.text(
            """
            INSERT INTO organizations (
                id,
                name,
                created_at
            )
            VALUES (
                :organization_id,
                'Default Organization',
                CURRENT_TIMESTAMP
            )
            """
        ).bindparams(_organization_id_bind())
    )

    # Add organization_id as nullable first so existing rows remain valid.

    op.add_column(
        "monitors",
        sa.Column(
            "organization_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.add_column(
        "notification_destinations",
        sa.Column(
            "organization_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.add_column(
        "outbox_events",
        sa.Column(
            "organization_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    op.add_column(
        "status_pages",
        sa.Column(
            "organization_id",
            sa.Uuid(),
            nullable=True,
        ),
    )

    # Move all resources from pre-organization versions into the
    # default organization.

    for table_name in (
        "monitors",
        "notification_destinations",
        "outbox_events",
        "status_pages",
    ):
        op.execute(
            sa.text(
                f"""
                UPDATE {table_name}
                SET organization_id = :organization_id
                WHERE organization_id IS NULL
                """
            ).bindparams(_organization_id_bind())
        )

    # After backfill every resource must belong to an organization.

    op.alter_column(
        "monitors",
        "organization_id",
        nullable=False,
    )

    op.alter_column(
        "notification_destinations",
        "organization_id",
        nullable=False,
    )

    op.alter_column(
        "outbox_events",
        "organization_id",
        nullable=False,
    )

    op.alter_column(
        "status_pages",
        "organization_id",
        nullable=False,
    )

    # Add indexes and foreign keys only after the data has been backfilled.

    op.create_index(
        "ix_monitors_organization_id",
        "monitors",
        ["organization_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_monitors_organization_id",
        "monitors",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_notification_destinations_organization_id",
        "notification_destinations",
        ["organization_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_notification_destinations_organization_id",
        "notification_destinations",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_outbox_events_organization_id",
        "outbox_events",
        ["organization_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_outbox_events_organization_id",
        "outbox_events",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.create_index(
        "ix_status_pages_organization_id",
        "status_pages",
        ["organization_id"],
        unique=False,
    )

    op.create_foreign_key(
        "fk_status_pages_organization_id",
        "status_pages",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    bind = op.get_bind()

    op.drop_constraint(
        "fk_status_pages_organization_id",
        "status_pages",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_status_pages_organization_id",
        table_name="status_pages",
    )
    op.drop_column(
        "status_pages",
        "organization_id",
    )

    op.drop_constraint(
        "fk_outbox_events_organization_id",
        "outbox_events",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_outbox_events_organization_id",
        table_name="outbox_events",
    )
    op.drop_column(
        "outbox_events",
        "organization_id",
    )

    op.drop_constraint(
        "fk_notification_destinations_organization_id",
        "notification_destinations",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_notification_destinations_organization_id",
        table_name="notification_destinations",
    )
    op.drop_column(
        "notification_destinations",
        "organization_id",
    )

    op.drop_constraint(
        "fk_monitors_organization_id",
        "monitors",
        type_="foreignkey",
    )
    op.drop_index(
        "ix_monitors_organization_id",
        table_name="monitors",
    )
    op.drop_column(
        "monitors",
        "organization_id",
    )

    op.drop_index(
        "ix_api_keys_organization_id",
        table_name="api_keys",
    )
    op.drop_index(
        "ix_api_keys_key_prefix",
        table_name="api_keys",
    )
    op.drop_table(
        "api_keys",
    )

    op.drop_index(
        "ix_memberships_user_id",
        table_name="memberships",
    )
    op.drop_index(
        "ix_memberships_organization_id",
        table_name="memberships",
    )
    op.drop_table(
        "memberships",
    )

    op.drop_index(
        "ix_users_email",
        table_name="users",
    )
    op.drop_table(
        "users",
    )

    op.drop_table(
        "organizations",
    )

    organization_role_enum.drop(
        bind,
        checkfirst=True,
    )
