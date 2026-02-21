from equiny.core.matching.domain.structures.dtos.swipe_dto import SwipeDto
from equiny.core.matching.domain.structures.swipe import Swipe
from equiny.database.sqlalchemy.models.matching.swipe_model import SwipeModel


class SwipesMapper:
    @staticmethod
    def to_entity(model: SwipeModel) -> Swipe:
        dto = SwipeDto(
            from_horse_id=model.from_horse_id,
            to_horse_id=model.to_horse_id,
            decision=model.decision,
            created_at=model.created_at,
            is_match=False,
        )
        return Swipe.create(dto)

    @staticmethod
    def to_model(swipe: Swipe) -> SwipeModel:
        dto = swipe.dto
        return SwipeModel(
            from_horse_id=dto.from_horse_id,
            to_horse_id=dto.to_horse_id,
            decision=dto.decision,
        )
