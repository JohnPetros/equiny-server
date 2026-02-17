from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.matching.domain.structures.dtos.match_dto import MatchDto
from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.matching.use_cases.list_matches_use_case import ListMatchesUseCase
from equiny.core.shared.responses.pagination_response import PaginationResponse
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe


class ListMatchesController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/matches',
            status_code=HTTPStatus.OK,
            response_model=PaginationResponse[MatchDto],
        )
        def _(
            horse_id: str,
            cursor: str | None = None,
            limit: int = 20,
            _: dict[str, str] = Depends(AuthPipe.verify_jwt),
            matches_repo: MatchesRepository = Depends(
                DatabasePipe.get_matches_repository
            ),
        ) -> PaginationResponse[MatchDto]:
            use_case = ListMatchesUseCase(matches_repo)
            return use_case.execute(horse_id, cursor, limit)
