from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends

from equiny.core.matching.use_cases.view_match_use_case import ViewHorseMatchUseCase
from equiny.core.profiling.domain.structures.dtos.horse_match_dto import HorseMatchDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe
from equiny.validation.shared import IdSchema
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.core.profiling.domain.entities.owner import Owner


repository = Annotated[HorsesRepository, Depends(DatabasePipe.get_horses_repository)]


class ViewHorseMatchController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.patch(
            '/{from_horse_id}/matches/{to_horse_id}',
            status_code=HTTPStatus.OK,
            dependencies=[Depends(AuthPipe.verify_jwt)],
            response_model=HorseMatchDto,
        )
        def _(
            from_horse_id: IdSchema,
            to_horse_id: IdSchema,
            owner: Annotated[Owner, Depends(ProfilingPipe.get_owner_id)],
            repository: repository,
        ) -> HorseMatchDto:
            use_case = ViewHorseMatchUseCase(repository)
            return use_case.execute(owner.id.value, from_horse_id, to_horse_id)
