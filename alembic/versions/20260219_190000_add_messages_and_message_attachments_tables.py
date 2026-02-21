"""add_messages_and_message_attachments_tables

Revision ID: 20260219_190000
Revises: a6e4632d5521
Create Date: 2026-02-19 19:00:00.000000

"""

from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260219_190000'
down_revision: str | None = 'a6e4632d5521'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        'messages',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('chat_id', sa.String(), nullable=False),
        sa.Column('sender_id', sa.String(), nullable=False),
        sa.Column('content', sa.String(), nullable=True),
        sa.Column('sent_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id']),
        sa.ForeignKeyConstraint(['sender_id'], ['owners.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_messages_chat_id'), 'messages', ['chat_id'], unique=False)
    op.create_index(
        op.f('ix_messages_sender_id'),
        'messages',
        ['sender_id'],
        unique=False,
    )
    op.create_index(op.f('ix_messages_sent_at'), 'messages', ['sent_at'], unique=False)
    op.create_index(
        'ix_messages_chat_id_id', 'messages', ['chat_id', 'id'], unique=False
    )

    op.create_table(
        'message_attachments',
        sa.Column('id', sa.String(), nullable=False),
        sa.Column('message_id', sa.String(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('kind', sa.String(), nullable=False),
        sa.Column('size', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['message_id'], ['messages.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(
        'ix_message_attachments_message_id',
        'message_attachments',
        ['message_id'],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        'ix_message_attachments_message_id',
        table_name='message_attachments',
    )
    op.drop_table('message_attachments')

    op.drop_index('ix_messages_chat_id_id', table_name='messages')
    op.drop_index(op.f('ix_messages_sent_at'), table_name='messages')
    op.drop_index(op.f('ix_messages_sender_id'), table_name='messages')
    op.drop_index(op.f('ix_messages_chat_id'), table_name='messages')
    op.drop_table('messages')
