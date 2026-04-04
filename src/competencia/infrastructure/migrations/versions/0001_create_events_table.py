"""Crear tabla events — Event Store BC Competencia (ADR-008).

Revision ID: 0001
Revises:
Create Date: 2026-03-21
"""

from __future__ import annotations

import sqlalchemy as sa

from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    op.create_table(
        "events",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("stream_id", sa.Text, nullable=False),
        sa.Column("event_type", sa.Text, nullable=False),
        sa.Column("payload", sa.Text, nullable=False),
        sa.Column("version", sa.Integer, nullable=False),
        sa.Column(
            "occurred_at",
            sa.Text,
            nullable=False,
            server_default=sa.text("(strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))"),
        ),
    )
    op.create_index("idx_events_stream_id_version", "events", ["stream_id", "version"])
    op.create_index(
        "uq_events_stream_version",
        "events",
        ["stream_id", "version"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("uq_events_stream_version", table_name="events")
    op.drop_index("idx_events_stream_id_version", table_name="events")
    op.drop_table("events")
