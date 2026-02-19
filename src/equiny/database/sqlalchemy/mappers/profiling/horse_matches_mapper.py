from datetime import datetime

from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.core.profiling.domain.structures.dtos.image_dto import ImageDto
from equiny.core.profiling.domain.structures.dtos.location_dto import LocationDto
from equiny.database.sqlalchemy.models.profiling.horse_model import HorseModel


class HorseMatchesMapper:
    @staticmethod
    def to_structure(
        horse_model: HorseModel, created_at: datetime, is_viewed: bool = False
    ) -> HorseMatch:
        owner_id = horse_model.owner_id or horse_model.id
        owner_name = (
            horse_model.owner.name if horse_model.owner is not None else 'Unknown owner'
        )
        owner_avatar = ImageDto(
            key=horse_model.owner.avatar_key or ''
            if horse_model.owner is not None
            else '',
            name=horse_model.owner.avatar_name or ''
            if horse_model.owner is not None
            else '',
        )
        owner_location = LocationDto(
            city=horse_model.location_city,
            state=horse_model.location_state,
        )

        return HorseMatch.create(
            HorseMatchDto(
                owner_id=owner_id,
                owner_name=owner_name,
                owner_avatar=owner_avatar,
                owner_location=owner_location,
                owner_horse_id=horse_model.id,
                created_at=created_at,
                is_viewed=is_viewed,
            )
        )
