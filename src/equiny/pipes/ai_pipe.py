from fastapi import Depends
from equiny.core.conversation.interfaces import GenerateIcebreakerWorkflow
from equiny.ai.agno.workfows.profiling.agno_generate_icebreaker_workflow import (
    AgnoGenerateIcebreakerWorkflow,
)
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.pipes.database_pipe import DatabasePipe


class AiPipe:
    @staticmethod
    def get_generate_icebreaker_workflow_from_request(
        horses_repository: HorsesRepository = Depends(
            DatabasePipe.get_horses_repository
        ),
    ) -> GenerateIcebreakerWorkflow:
        return AgnoGenerateIcebreakerWorkflow(horses_repository)
