"""create initial tables

Revision ID: 0001
Revises:
Create Date: 2026-05-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("email", sa.String(), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"])

    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_rooms_id", "rooms", ["id"])

    op.create_table(
        "measurements",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("room_id", sa.Integer(), sa.ForeignKey("rooms.id"), nullable=False),
        sa.Column("download_mbps", sa.Float(), nullable=False),
        sa.Column("upload_mbps", sa.Float(), nullable=False),
        sa.Column("ping_ms", sa.Float(), nullable=False),
        sa.Column("jitter_ms", sa.Float(), nullable=False),
        sa.Column("measured_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_measurements_id", "measurements", ["id"])


def downgrade() -> None:
    op.drop_index("ix_measurements_id", table_name="measurements")
    op.drop_table("measurements")
    op.drop_index("ix_rooms_id", table_name="rooms")
    op.drop_table("rooms")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_index("ix_users_id", table_name="users")
    op.drop_table("users")
