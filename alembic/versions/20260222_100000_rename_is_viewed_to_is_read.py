"""rename_is_viewed_to_is_read

Revision ID: 20260222_100000
Revises: 20260221_210000
Create Date: 2026-02-22 10:00:00.000000

"""

from collections.abc import Sequence

from alembic import op


revision: str = '20260222_100000'
down_revision: str | None = '20260221_210000'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column(
        'messages',
        'is_viewed_by_recipient',
        new_column_name='is_read_by_recipient',
    )


def downgrade() -> None:
    op.alter_column(
        'messages',
        'is_read_by_recipient',
        new_column_name='is_viewed_by_recipient',
    )
