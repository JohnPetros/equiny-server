from typing import Protocol
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.logical import Logical


class OwnersRepository(Protocol):
    def add(self, owner: Owner) -> None: ...

    def add_many(self, owners: list[Owner]) -> None: ...

    def find_by_id(self, owner_id: Id) -> Owner | None: ...

    def find_by_account_id(self, account_id: Id) -> Owner | None: ...

    def update_has_completed_onboarding(
        self,
        owner_id: Id,
        has_completed_onboarding: Logical,
    ) -> None: ...
