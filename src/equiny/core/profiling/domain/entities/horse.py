from equiny.core.profiling.domain.structures.location import Location
from equiny.core.shared.domain.decorators import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.profiling.domain.entities.dtos.horse_dto import HorseDto
from equiny.core.profiling.domain.structures.breed import Breed
from equiny.core.profiling.domain.structures.horse_birth import HorseBirth
from equiny.core.profiling.domain.structures.sex import Sex
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.name import Name
from equiny.core.shared.domain.structures.decimal import Decimal
from equiny.core.shared.domain.structures.logical import Logical
from equiny.core.shared.domain.structures.text import Text


@entity
class Horse(Entity):
    name: Name
    birth: HorseBirth
    breed: Breed
    description: Text | None
    height: Decimal
    sex: Sex
    location: Location
    is_active: Logical

    @classmethod
    def create(cls, dto: HorseDto) -> 'Horse':
        return cls(
            id=Id.create(dto.id),
            name=Name.create(dto.name),
            birth=HorseBirth.create(dto.birth_month, dto.birth_year),
            breed=Breed.create(dto.breed),
            description=Text.create(dto.description) if dto.description else None,
            height=Decimal.create(dto.height),
            sex=Sex.create(dto.sex),
            location=Location.create(dto.location),
            is_active=Logical.create(dto.is_active),
        )

    def toggle_activation(self) -> None:
        self.is_active = self.is_active.invert()

    @property
    def dto(self) -> HorseDto:
        return HorseDto(
            id=self.id.value,
            name=self.name.value,
            birth_month=self.birth.month,
            birth_year=self.birth.year,
            description=self.description.value if self.description else '',
            height=self.height.value,
            breed=self.breed.dto,
            sex=self.sex.dto,
            location=self.location.dto,
            is_active=self.is_active.value,
        )
