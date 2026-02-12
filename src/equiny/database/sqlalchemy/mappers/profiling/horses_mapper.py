from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.domain.structures.breed import BreedValue
from equiny.database.sqlalchemy.models.profiling.horse_model import HorseModel


class HorsesMapper:
    @staticmethod
    def to_entity(horse_model: HorseModel) -> Horse:
        return Horse.create(HorsesMapper.to_dto(horse_model))

    @staticmethod
    def to_dto(horse_model: HorseModel) -> HorseDto:
        return HorseDto(
            id=horse_model.id,
            name=horse_model.name,
            birth_month=horse_model.birth_month,
            birth_year=horse_model.birth_year,
            breed=horse_model.breed.value,
        )

    @staticmethod
    def to_model(horse: Horse) -> HorseModel:
        horse_dto = horse.dto
        return HorseModel(
            id=horse_dto.id,
            name=horse_dto.name,
            birth_month=horse_dto.birth_month,
            birth_year=horse_dto.birth_year,
            breed=BreedValue(horse_dto.breed),
        )
