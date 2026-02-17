from equiny.core.matching.domain.structures.swipe import Swipe
from equiny.core.matching.interfaces.swipes_repository import SwipesRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.database.sqlalchemy.mappers.matching.swipes_mapper import SwipesMapper
from equiny.database.sqlalchemy.models.matching.swipe_model import SwipeModel
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)


class SqlalchemySwipesRepository(SqlalchemyRepository, SwipesRepository):
    def add(self, swipe: Swipe) -> None:
        model = SwipesMapper.to_model(swipe)
        self.sqlalchemy.add(model)

    def find_by_to_horse_id(self, to_horse_id: Id) -> Swipe | None:
        model = (
            self.sqlalchemy.query(SwipeModel)
            .filter(SwipeModel.to_horse_id == to_horse_id.value)
            .first()
        )
        if model is None:
            return None
        return SwipesMapper.to_entity(model)

    def find_by_horses(self, from_horse_id: Id, to_horse_id: Id) -> Swipe | None:
        model = (
            self.sqlalchemy.query(SwipeModel)
            .filter(SwipeModel.from_horse_id == from_horse_id.value)
            .filter(SwipeModel.to_horse_id == to_horse_id.value)
            .first()
        )
        if model is None:
            return None
        return SwipesMapper.to_entity(model)
