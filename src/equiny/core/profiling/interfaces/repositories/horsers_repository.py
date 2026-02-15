from typing import Protocol
from equiny.core.profiling.domain.entities.horse import Horse
from equiny.core.profiling.domain.structures.image import Image
from equiny.core.shared.domain.structures.id import Id


class HorsesRepository(Protocol):
    def add(self, horse: Horse, owner_id: Id) -> None: ...

    def add_many(self, horses: list[Horse], owner_id: Id) -> None: ...

    def find_by_id(self, horse_id: Id) -> Horse | None: ...

    def add_many_images(self, horse_id: Id, images: list[Image]) -> None: ...
