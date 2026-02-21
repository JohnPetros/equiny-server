from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from equiny.database.sqlalchemy.models.model import Model


class AttachmentModel(Model):
    __tablename__ = 'message_attachments'

    id: Mapped[str] = mapped_column(primary_key=True)
    message_id: Mapped[str] = mapped_column(ForeignKey('messages.id'))
    key: Mapped[str]
    name: Mapped[str]
    kind: Mapped[str]
    size: Mapped[float]

    __table_args__ = (Index('ix_message_attachments_message_id', 'message_id'),)
