from datetime import datetime

from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.fakers.profiling.structures.image_faker import ImageFaker
from equiny.fakers.profiling.structures.location_faker import LocationFaker
from equiny.fakers.shared.structures.id_faker import IdFaker


class HorseMatchFaker:
    @staticmethod
    def fake(
        owner_id: str | None = None,
        owner_name: str | None = None,
        owner_horse_id: str | None = None,
        created_at: datetime | None = None,
        is_viewed: bool = False,
    ) -> HorseMatch:
        return HorseMatch.create(
            HorseMatchFaker.fake_dto(
                owner_id=owner_id,
                owner_name=owner_name,
                owner_horse_id=owner_horse_id,
                created_at=created_at,
                is_viewed=is_viewed,
            )
        )

    @staticmethod
    def fake_dto(
        owner_id: str | None = None,
        owner_name: str | None = None,
        owner_horse_id: str | None = None,
        created_at: datetime | None = None,
        is_viewed: bool = False,
    ) -> HorseMatchDto:
        return HorseMatchDto(
            owner_id=owner_id or IdFaker.fake().value,
            owner_name=owner_name or 'Owner Faker',
            owner_avatar=ImageFaker.fake_dto(),
            owner_location=LocationFaker.fake_dto(),
            owner_horse_id=owner_horse_id or IdFaker.fake().value,
            created_at=created_at or datetime.now(),
            is_viewed=is_viewed,
        )
