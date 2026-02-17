from uuid import uuid4

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from equiny.database.sqlalchemy.models.model import Model


class SwipeModel(Model):
    __tablename__ = 'swipes'
    __table_args__ = (
        UniqueConstraint('from_horse_id', 'to_horse_id', name='uq_swipe_pair'),
    )

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: uuid4().hex)
    from_horse_id: Mapped[str] = mapped_column(ForeignKey('horses.id'), index=True)
    to_horse_id: Mapped[str] = mapped_column(ForeignKey('horses.id'), index=True)
    decision: Mapped[str]
