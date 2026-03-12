from fastapi import Depends

from equiny.core.conversation.interfaces import GenerateIcebreakerWorkflow
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.pipes.database_pipe import DatabasePipe


class _LazyGenerateIcebreakerWorkflow:
    def __init__(self, horses_repository: HorsesRepository) -> None:
        self._horses_repository = horses_repository

    def run(self, sender_id: str, recipient_id: str) -> str:
        from equiny.ai.agno.workflows.profiling.agno_generate_icebreaker_workflow import (
            AgnoGenerateIcebreakerWorkflow,
        )

        workflow = AgnoGenerateIcebreakerWorkflow(self._horses_repository)
        return workflow.run(sender_id=sender_id, recipient_id=recipient_id)


class AiPipe:
    @staticmethod
    def get_generate_icebreaker_workflow_from_request(
        horses_repository: HorsesRepository = Depends(
            DatabasePipe.get_horses_repository
        ),
    ) -> GenerateIcebreakerWorkflow:
        return _LazyGenerateIcebreakerWorkflow(horses_repository)
