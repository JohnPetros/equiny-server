"""add_is_viewed_by_recipient_to_messages

Revision ID: 20260220_120000
Revises: 20260219_190000
Create Date: 2026-02-20 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260220_120000'
down_revision: str | None = '20260219_190000'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    dialect_name = op.get_bind().dialect.name

    op.add_column(
        'messages',
        sa.Column(
            'is_viewed_by_recipient',
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )

    if dialect_name != 'sqlite':
        op.alter_column('messages', 'is_viewed_by_recipient', server_default=None)


def downgrade() -> None:
    op.drop_column('messages', 'is_viewed_by_recipient')
