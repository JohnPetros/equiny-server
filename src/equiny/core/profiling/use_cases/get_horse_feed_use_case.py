from equiny.core.profiling.domain.structures.breed import Breed
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.domain.structures.dtos.age_range_dto import AgeRangeDto
from equiny.core.profiling.domain.structures.dtos.location_dto import LocationDto
from equiny.core.profiling.domain.structures.dtos.feed_horse_dto import FeedHorseDto
from equiny.core.profiling.domain.structures.sex import Sex
from equiny.core.profiling.domain.structures.age_range import AgeRange
from equiny.core.profiling.domain.structures.location import Location
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.responses.pagination_response import PaginationResponse


class GetHorseFeedUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self._repository = repository

    def execute(
        self,
        horse_id: str,
        sex: str,
        breeds: list[str],
        age_range_dto: AgeRangeDto,
        location_dto: LocationDto,
        cursor: str | None = None,
        limit: int = 20,
    ) -> PaginationResponse[FeedHorseDto]:
        cursor_id = Id.create(cursor) if cursor else None

        pagination_response = self._repository.find_many_feed_horses(
            horse_id=Id.create(horse_id),
            sex=Sex.create(sex),
            age_range=AgeRange.create(age_range_dto),
            breeds=[Breed.create(breed) for breed in breeds],
            location=Location.create(location_dto),
            cursor=cursor_id,
            limit=limit,
        )

        return pagination_response.map_items(lambda feed_horse: feed_horse.dto)
