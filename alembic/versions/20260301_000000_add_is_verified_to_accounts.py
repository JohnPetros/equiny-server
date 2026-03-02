"""add_is_verified_to_accounts

Revision ID: 20260301_000000
Revises: 20260222_100000
Create Date: 2026-03-01 00:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260301_000000'
down_revision: str | None = 'a6e4632d5521'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        'accounts',
        sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='false'),
    )


def downgrade() -> None:
    op.drop_column('accounts', 'is_verified')
