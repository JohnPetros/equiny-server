from typing import Protocol
from equiny.core.profiling.domain.entities.horse import Horse


class HorsesRepository(Protocol):
    def add(self, horse: Horse) -> None: ...

    def find_by_id(self, horse_id: str) -> Horse | None: ...
