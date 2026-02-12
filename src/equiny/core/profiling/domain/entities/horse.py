from equiny.core.shared.domain.decorators import entity
from equiny.core.shared.domain.abstracts import Entity
from equiny.core.profiling.domain.entities.dtos.horse_dto import HorseDto
from equiny.core.profiling.domain.structures.breed import Breed
from equiny.core.profiling.domain.structures.horse_birth import HorseBirth
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.name import Name


@entity
class Horse(Entity):
    name: Name
    birth: HorseBirth
    breed: Breed

    @classmethod
    def create(cls, dto: HorseDto) -> 'Horse':
        return cls(
            id=Id.create(dto.id),
            name=Name.create(dto.name),
            birth=HorseBirth.create(dto.birth_month, dto.birth_year),
            breed=Breed.create_as_arabe(),
        )

    @property
    def dto(self) -> HorseDto:
        return HorseDto(
            id=self.id.value,
            name=self.name.value,
            birth_month=self.birth.month,
            birth_year=self.birth.year,
            breed=self.breed.dto,
        )
