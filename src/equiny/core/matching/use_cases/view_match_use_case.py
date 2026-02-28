from equiny.core.profiling.domain.errors.horse_match_not_found_error import (
    HorseMatchNotFoundError,
)
from equiny.core.profiling.domain.errors.horse_not_found_error import HorseNotFoundError
from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.profiling.domain.structures.horse_match import HorseMatch
from equiny.core.profiling.domain.entities.horse import Horse


class ViewHorseMatchUseCase:
    def __init__(self, repository: HorsesRepository) -> None:
        self._repository = repository

    def execute(
        self, owner_id: str, from_horse_id: str, to_horse_id: str
    ) -> HorseMatchDto:
        from_horse = self._find_horse(Id.create(owner_id), Id.create(from_horse_id))
        horse_match = self._find_horse_match(from_horse.id, Id.create(to_horse_id))
        viewed_horse_match = horse_match.view()
        self._repository.replace_horse_match(
            from_horse.id, Id.create(to_horse_id), viewed_horse_match
        )
        return viewed_horse_match.dto

    def _find_horse(self, owner_id: Id, horse_id: Id) -> Horse:
        horse = self._repository.find_by_id_and_owner_id(horse_id, owner_id)
        if horse is None:
            raise HorseNotFoundError
        return horse

    def _find_horse_match(self, from_horse_id: Id, to_horse_id: Id) -> HorseMatch:
        horse_match = self._repository.find_horse_match_by_horses(
            from_horse_id, to_horse_id
        )
        if horse_match is None:
            raise HorseMatchNotFoundError
        return horse_match
