from typing import TYPE_CHECKING
from uuid import uuid4

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from equiny.database.sqlalchemy.models.model import Model

if TYPE_CHECKING:
    from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel


class ChatModel(Model):
    __tablename__ = 'chats'

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: uuid4().hex)
    owner_a_id: Mapped[str] = mapped_column(ForeignKey('owners.id'), index=True)
    owner_b_id: Mapped[str] = mapped_column(ForeignKey('owners.id'), index=True)

    owner_a: Mapped['OwnerModel'] = relationship(foreign_keys=[owner_a_id])
    owner_b: Mapped['OwnerModel'] = relationship(foreign_keys=[owner_b_id])

    __table_args__ = (
        Index('ix_chats_owners_pair', 'owner_a_id', 'owner_b_id', unique=True),
    )
