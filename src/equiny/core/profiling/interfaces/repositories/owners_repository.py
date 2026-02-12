from typing import Protocol
from equiny.core.profiling.domain.entities.owner import Owner


class OwnersRepository(Protocol):
    def add(self, owner: Owner) -> None: ...

    def find_by_id(self, owner_id: str) -> Owner | None: ...
