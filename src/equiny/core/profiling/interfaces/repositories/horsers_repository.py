from typing import Protocol
from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.structures.gallery import Gallery
from equiny.core.shared.domain.structures.image import Image
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.domain.structures.location import Location
from equiny.core.profiling.domain.structures.breed import Breed
from equiny.core.profiling.domain.structures.sex import Sex
from equiny.core.profiling.domain.structures.age_range import AgeRange
from equiny.core.shared.responses.pagination_response import PaginationResponse
from equiny.core.profiling.domain.structures.feed_horse import FeedHorse
from equiny.core.profiling.domain.structures.horse_match import HorseMatch


class HorsesRepository(Protocol):
    def add(self, horse: Horse, owner_id: Id) -> None: ...

    def find_many_feed_horses(
        self,
        horse_id: Id,
        sex: Sex,
        age_range: AgeRange,
        breeds: list[Breed],
        location: Location,
        cursor: Id | None = None,
        limit: int = 20,
    ) -> PaginationResponse[FeedHorse]: ...

    def add_many(self, horses: list[Horse], owner_id: Id) -> None: ...

    def find_by_id(self, horse_id: Id) -> Horse | None: ...

    def find_by_id_and_owner_id(self, horse_id: Id, owner_id: Id) -> Horse | None: ...

    def find_all_matches(self, horse_id: Id) -> list[HorseMatch]: ...

    def find_many_by_owner(self, owner_id: Id) -> list[Horse]: ...

    def find_horse_match_by_horses(
        self, from_horse_id: Id, to_horse_id: Id
    ) -> HorseMatch | None: ...

    def find_horse_matches_by_owner_id(self, owner_id: Id) -> list[HorseMatch]: ...

    def add_many_images(self, horse_id: Id, images: list[Image]) -> None: ...

    def find_gallery_by_horse_id(self, horse_id: Id) -> Gallery | None: ...

    def replace(self, horse: Horse) -> None: ...

    def replace_horse_match(
        self, from_horse_id: Id, to_horse_id: Id, horse_match: HorseMatch
    ) -> None: ...

    def delete_many_images(self, horse_id: Id) -> None: ...
