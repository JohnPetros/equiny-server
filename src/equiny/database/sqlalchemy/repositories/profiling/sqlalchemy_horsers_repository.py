from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.database.sqlalchemy.mappers.profiling.horses_mapper import HorsesMapper
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)
from equiny.database.sqlalchemy.models.profiling.horse_model import HorseModel


class SqlalchemyHorsesRepository(SqlalchemyRepository, HorsesRepository):
    def add(self, horse: Horse) -> None:
        horse_model = HorsesMapper.to_model(horse)
        self.sqlalchemy.add(horse_model)

    def find_by_id(self, horse_id: str) -> Horse | None:
        horse_model = (
            self.sqlalchemy.query(HorseModel).filter(HorseModel.id == horse_id).first()
        )
        if horse_model is None:
            return None
        return HorsesMapper.to_entity(horse_model)
