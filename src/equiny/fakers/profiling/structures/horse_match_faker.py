from datetime import datetime

from faker import Faker

from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.fakers.profiling.structures.image_faker import ImageFaker
from equiny.fakers.profiling.structures.location_faker import LocationFaker
from equiny.fakers.shared.structures.id_faker import IdFaker


class HorseMatchFaker:
    _faker = Faker()

    @staticmethod
    def fake(
        owner_id: str | None = None,
        owner_name: str | None = None,
        owner_horse_id: str | None = None,
        owner_horse_name: str | None = None,
        created_at: datetime | None = None,
        is_viewed: bool = False,
    ) -> HorseMatch:
        return HorseMatch.create(
            HorseMatchFaker.fake_dto(
                owner_id=owner_id,
                owner_name=owner_name,
                owner_horse_id=owner_horse_id,
                owner_horse_name=owner_horse_name,
                created_at=created_at,
                is_viewed=is_viewed,
            )
        )

    @staticmethod
    def fake_dto(
        owner_id: str | None = None,
        owner_name: str | None = None,
        owner_horse_id: str | None = None,
        owner_horse_name: str | None = None,
        created_at: datetime | None = None,
        is_viewed: bool = False,
    ) -> HorseMatchDto:
        return HorseMatchDto(
            owner_id=owner_id or IdFaker.fake().value,
            owner_name=owner_name or 'Owner Faker',
            owner_avatar=ImageFaker.fake_dto(),
            owner_location=LocationFaker.fake_dto(),
            owner_horse_id=owner_horse_id or IdFaker.fake().value,
            owner_horse_name=owner_horse_name or HorseMatchFaker._faker.first_name(),
            owner_horse_image=ImageFaker.fake_dto(),
            created_at=created_at or datetime.now(),
            is_viewed=is_viewed,
        )
