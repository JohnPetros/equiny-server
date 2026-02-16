"""add_horse_sex_and_location_columns

Revision ID: 4f1b05aff958
Revises: 8eb376d301fe
Create Date: 2026-02-15 16:00:00.942335

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f1b05aff958'
down_revision: Union[str, None] = '8eb376d301fe'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    sex_enum = sa.Enum('MALE', 'FEMALE', name='sexvalue')
    sex_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        'horses',
        sa.Column('sex', sex_enum, nullable=False, server_default='MALE'),
    )
    op.add_column(
        'horses',
        sa.Column('location_city', sa.String(), nullable=False, server_default=''),
    )
    op.add_column(
        'horses',
        sa.Column('location_state', sa.String(), nullable=False, server_default=''),
    )

    op.alter_column('horses', 'sex', server_default=None)
    op.alter_column('horses', 'location_city', server_default=None)
    op.alter_column('horses', 'location_state', server_default=None)


def downgrade() -> None:
    op.drop_column('horses', 'location_state')
    op.drop_column('horses', 'location_city')
    op.drop_column('horses', 'sex')

    sa.Enum('MALE', 'FEMALE', name='sexvalue').drop(op.get_bind(), checkfirst=True)
