from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from equiny.database.sqlalchemy.models.model import Model
from equiny.core.profiling.domain.structures.breed import BreedValue

if TYPE_CHECKING:
    from equiny.database.sqlalchemy.models.profiling.horse_image_model import (
        HorseImageModel,
    )


class HorseModel(Model):
    __tablename__ = 'horses'

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    birth_month: Mapped[int]
    birth_year: Mapped[int]
    breed: Mapped[BreedValue]

    images: Mapped[list['HorseImageModel']] = relationship(
        back_populates='horse',
        cascade='all, delete-orphan',
    )
