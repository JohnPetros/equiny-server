"""add_social_accounts_and_nullable_password

Revision ID: 20260314_120000
Revises: 20260301_000000
Create Date: 2026-03-14 12:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = '20260314_120000'
down_revision: str | None = '20260301_000000'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.alter_column('accounts', 'password', existing_type=sa.String(), nullable=True)
    op.create_table(
        'social_accounts',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('account_id', sa.String(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('provider', sa.String(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('account_id', 'provider'),
        sa.UniqueConstraint('provider', 'email'),
    )
    op.create_index(
        op.f('ix_social_accounts_account_id'),
        'social_accounts',
        ['account_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f('ix_social_accounts_account_id'), table_name='social_accounts')
    op.drop_table('social_accounts')
    op.alter_column('accounts', 'password', existing_type=sa.String(), nullable=False)
