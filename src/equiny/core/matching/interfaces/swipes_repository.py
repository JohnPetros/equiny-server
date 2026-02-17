from typing import Protocol

from equiny.core.matching.domain.structures.swipe import Swipe
from equiny.core.shared.domain.structures.id import Id


class SwipesRepository(Protocol):
    def add(self, swipe: Swipe) -> None: ...

    def find_by_to_horse_id(self, to_horse_id: Id) -> Swipe | None: ...

    def find_by_horses(self, from_horse_id: Id, to_horse_id: Id) -> Swipe | None: ...
