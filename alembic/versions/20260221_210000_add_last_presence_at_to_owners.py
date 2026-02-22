"""add_last_presence_at_to_owners

Revision ID: 20260221_210000
Revises: 20260220_120000
Create Date: 2026-02-21 21:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260221_210000'
down_revision: str | None = '20260220_120000'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column('owners', sa.Column('last_presence_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('owners', 'last_presence_at')
