from uuid import uuid4

from sqlalchemy import ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column

from equiny.database.sqlalchemy.models.model import Model


class MatchModel(Model):
    __tablename__ = 'matches'

    id: Mapped[str] = mapped_column(primary_key=True, default=lambda: uuid4().hex)
    horse_a_id: Mapped[str] = mapped_column(ForeignKey('horses.id'), index=True)
    horse_b_id: Mapped[str] = mapped_column(ForeignKey('horses.id'), index=True)
    has_horse_a_viewed: Mapped[bool] = mapped_column(default=False, nullable=False)
    has_horse_b_viewed: Mapped[bool] = mapped_column(default=False, nullable=False)

    __table_args__ = (
        Index('ix_matches_pair', 'horse_a_id', 'horse_b_id', unique=True),
    )
