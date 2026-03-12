from agno.tools import Toolkit

from equiny.core.profiling.domain.entities.dtos import HorseDto
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.get_horse_use_case import GetHorseUseCase
from equiny.validation.shared import IdSchema


class ProfilingToolkit(Toolkit):
    def __init__(self, repository: HorsesRepository) -> None:
        super().__init__(
            name='Profiling Toolkit',
            tools=[self.get_horse_tool],
        )
        self._repository = repository

    def get_horse_tool(self, horse_id: IdSchema) -> HorseDto:
        """
        Get a horse by its ID.

        Args:
            horse_id: The unique ID of the horse.

        Returns:
            Horse DTO.
        """
        use_case = GetHorseUseCase(self._repository)
        return use_case.execute(horse_id)
