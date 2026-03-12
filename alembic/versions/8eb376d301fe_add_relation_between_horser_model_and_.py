"""add relation between horser model and owner model

Revision ID: 8eb376d301fe
Revises: 48a95422cca7
Create Date: 2026-02-15 15:50:48.152818

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8eb376d301fe'
down_revision: Union[str, None] = '48a95422cca7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    dialect_name = op.get_bind().dialect.name

    if dialect_name == 'sqlite':
        with op.batch_alter_table('horses') as batch_op:
            batch_op.add_column(sa.Column('owner_id', sa.String(), nullable=True))
            batch_op.create_foreign_key(
                'fk_horses_owner_id_owners',
                'owners',
                ['owner_id'],
                ['id'],
            )
        return

    op.add_column('horses', sa.Column('owner_id', sa.String(), nullable=True))
    op.create_foreign_key(
        'fk_horses_owner_id_owners',
        'horses',
        'owners',
        ['owner_id'],
        ['id'],
    )


def downgrade() -> None:
    dialect_name = op.get_bind().dialect.name

    if dialect_name == 'sqlite':
        with op.batch_alter_table('horses') as batch_op:
            batch_op.drop_constraint('fk_horses_owner_id_owners', type_='foreignkey')
            batch_op.drop_column('owner_id')
        return

    op.drop_constraint('fk_horses_owner_id_owners', 'horses', type_='foreignkey')
    op.drop_column('horses', 'owner_id')
