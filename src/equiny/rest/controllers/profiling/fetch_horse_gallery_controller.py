from http import HTTPStatus
from fastapi import APIRouter, Depends
from typing import Annotated

from equiny.core.profiling.domain.structures.dtos import GalleryDto
from equiny.core.profiling.use_cases.get_horse_gallery import GetHorseGalleryUseCase
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.pipes import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.validation.profiling.gallery_schema import GallerySchema


repository = Annotated[HorsesRepository, Depends(DatabasePipe.get_horses_repository)]


class FetchHorseGalleryController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/{horse_id}/gallery',
            status_code=HTTPStatus.OK,
            response_model=GallerySchema,
        )
        def _(
            horse_id: str,
            repository: repository,
            owner: Owner = Depends(ProfilingPipe.get_owner),
        ) -> GalleryDto:
            use_case = GetHorseGalleryUseCase(repository)
            return use_case.execute(owner.id.value, horse_id)
