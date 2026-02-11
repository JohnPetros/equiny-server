from abc import ABC, abstractmethod
from equiny.core.profiling.domain.entities.horse import Horse


class HorsesRepository(ABC):
    @abstractmethod
    def add(self, horse: Horse) -> None: ...

    @abstractmethod
    def find_by_id(self, horse_id: str) -> Horse | None: ...
