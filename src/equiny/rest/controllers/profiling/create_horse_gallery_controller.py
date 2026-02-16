from http import HTTPStatus
from fastapi import APIRouter, Depends

from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.domain.structures.dtos import GalleryDto
from equiny.core.profiling.interfaces.repositories import (
    HorsesRepository,
    OwnersRepository,
)
from equiny.core.profiling.use_cases.create_horse_gallery_use_case import (
    CreateHorseGalleryUseCase,
)
from equiny.pipes.database_pipe import DatabasePipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.validation.profiling.gallery_schema import GallerySchema


class CreateHorseGalleryController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/{horse_id}/gallery',
            status_code=HTTPStatus.CREATED,
            response_model=GallerySchema,
        )
        def _(
            body: GallerySchema,
            horse_id: str,
            owner: Owner = Depends(ProfilingPipe.get_owner),
            horses_repository: HorsesRepository = Depends(
                DatabasePipe.get_horses_repository
            ),
            owners_repository: OwnersRepository = Depends(
                DatabasePipe.get_owners_repository
            ),
        ) -> GalleryDto:
            use_case = CreateHorseGalleryUseCase(horses_repository, owners_repository)
            return use_case.execute(horse_id, owner.id.value, body.to_dto().images)
