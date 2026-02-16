from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.entities.dtos.owner_dto import OwnerDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.pipes.profiling_pipe import ProfilingPipe


class FetchOwnerController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/me',
            status_code=HTTPStatus.OK,
            response_model=OwnerDto,
        )
        def _(
            owner: Owner = Depends(ProfilingPipe.get_owner),
        ) -> OwnerDto:
            return owner.dto
