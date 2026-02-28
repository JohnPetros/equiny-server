from http import HTTPStatus

from fastapi import APIRouter, Depends

from equiny.core.matching.domain.structures.dtos.swipe_dto import SwipeDto
from equiny.core.matching.interfaces.matches_repository import MatchesRepository
from equiny.core.matching.interfaces.swipes_repository import SwipesRepository
from equiny.core.matching.use_cases.swipe_horse_use_case import SwipeHorseUseCase
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.interfaces.broker import Broker
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.pubsub_pipe import PubSubPipe
from equiny.validation.matching.swipe_schema import SwipeSchema


class SwipeHorseController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/',
            status_code=HTTPStatus.CREATED,
            response_model=SwipeDto,
        )
        def _(
            body: SwipeSchema,
            _: dict[str, str] = Depends(AuthPipe.verify_jwt),
            swipes_repo: SwipesRepository = Depends(DatabasePipe.get_swipes_repository),
            matches_repo: MatchesRepository = Depends(
                DatabasePipe.get_matches_repository
            ),
            horses_repo: HorsesRepository = Depends(DatabasePipe.get_horses_repository),
            broker: Broker = Depends(PubSubPipe.get_redis_matching_broker),
        ) -> SwipeDto:
            use_case = SwipeHorseUseCase(swipes_repo, matches_repo, horses_repo, broker)
            return use_case.execute(body.to_dto())
