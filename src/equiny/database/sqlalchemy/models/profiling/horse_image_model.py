from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from equiny.database.sqlalchemy.models.model import Model


class HorseImageModel(Model):
    __tablename__ = 'horse_images'

    id: Mapped[str] = mapped_column(primary_key=True)
    horse_id: Mapped[str] = mapped_column(
        ForeignKey('horses.id', ondelete='CASCADE'),
        index=True,
    )
    key: Mapped[str]
    name: Mapped[str]
    position: Mapped[int]

    horse: Mapped['HorseModel'] = relationship(back_populates='images')
