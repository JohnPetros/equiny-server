from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from equiny.database.sqlalchemy.models.model import Model
from equiny.core.profiling.domain.structures.breed import BreedValue
from equiny.core.profiling.domain.structures.sex import SexValue

if TYPE_CHECKING:
    from equiny.database.sqlalchemy.models.profiling.horse_image_model import (
        HorseImageModel,
    )
    from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel


class HorseModel(Model):
    __tablename__ = 'horses'

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    description: Mapped[str | None] = mapped_column(nullable=True)
    birth_month: Mapped[int]
    birth_year: Mapped[int]
    height: Mapped[float]
    breed: Mapped[BreedValue]
    sex: Mapped[SexValue]
    location_city: Mapped[str]
    location_state: Mapped[str]
    location_latitude: Mapped[float] = mapped_column(default=0.0)
    location_longitude: Mapped[float] = mapped_column(default=0.0)
    owner_id: Mapped[str | None] = mapped_column(
        ForeignKey('owners.id'),
        nullable=True,
        default=None,
    )
    is_active: Mapped[bool] = mapped_column(default=True)

    owner: Mapped['OwnerModel | None'] = relationship(back_populates='horses')
    images: Mapped[list['HorseImageModel']] = relationship(
        back_populates='horse',
        cascade='all, delete-orphan',
    )
