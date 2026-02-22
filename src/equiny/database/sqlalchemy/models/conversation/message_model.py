from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from equiny.database.sqlalchemy.models.model import Model

if TYPE_CHECKING:
    from equiny.database.sqlalchemy.models.conversation.attachment_model import (
        AttachmentModel,
    )


class MessageModel(Model):
    __tablename__ = 'messages'

    id: Mapped[str] = mapped_column(primary_key=True)
    chat_id: Mapped[str] = mapped_column(ForeignKey('chats.id'), index=True)
    sender_id: Mapped[str] = mapped_column(ForeignKey('owners.id'), index=True)
    content: Mapped[str | None]
    is_read_by_recipient: Mapped[bool] = mapped_column(default=False)
    sent_at: Mapped[datetime] = mapped_column(index=True)

    attachments: Mapped[list['AttachmentModel']] = relationship(
        cascade='all, delete-orphan'
    )

    __table_args__ = (Index('ix_messages_chat_id_id', 'chat_id', 'id'),)
