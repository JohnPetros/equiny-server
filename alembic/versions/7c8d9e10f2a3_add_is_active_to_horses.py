"""add_is_active_to_horses

Revision ID: 7c8d9e10f2a3
Revises: 61df63cbfb44
Create Date: 2026-02-16 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c8d9e10f2a3'
down_revision: Union[str, None] = '61df63cbfb44'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    dialect_name = op.get_bind().dialect.name

    op.add_column(
        'horses',
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='false'),
    )

    if dialect_name != 'sqlite':
        op.alter_column('horses', 'is_active', server_default=None)


def downgrade() -> None:
    op.drop_column('horses', 'is_active')
