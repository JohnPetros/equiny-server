from http import HTTPStatus

from fastapi import APIRouter

from equiny.core.profiling.domain.structures.breed import BreedValue
from equiny.core.shared.responses.list_response import ListResponse


class FetchBreedsController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.get(
            '/breeds',
            status_code=HTTPStatus.OK,
            response_model=ListResponse[str],
        )
        def _() -> ListResponse[str]:
            breeds = [breed.value for breed in BreedValue]
            return ListResponse(items=breeds)
