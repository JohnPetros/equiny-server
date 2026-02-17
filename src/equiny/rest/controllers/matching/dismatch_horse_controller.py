from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.matching.use_cases.dismatch_horse_use_case import DismatchHorseUseCase
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.validation.shared.id_schema import IdSchema


class DismatchHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.delete(
            '/matches',
            status_code=HTTPStatus.NO_CONTENT,
        )
        def _(
            horse_a_id: IdSchema,
            horse_b_id: IdSchema,
            _: dict[str, str] = Depends(AuthPipe.verify_jwt),
            matches_repo: MatchesRepository = Depends(
                DatabasePipe.get_matches_repository
            ),
        ) -> None:
            use_case = DismatchHorseUseCase(matches_repo)
            use_case.execute(horse_a_id, horse_b_id)
