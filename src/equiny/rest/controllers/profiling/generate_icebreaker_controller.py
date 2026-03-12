from http import HTTPStatus

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from equiny.core.conversation.interfaces import GenerateIcebreakerWorkflow
from equiny.core.shared.domain.structures.id import Id
from equiny.pipes.ai_pipe import AiPipe
from equiny.pipes.profiling_pipe import ProfilingPipe
from equiny.validation.shared.id_schema import IdSchema


class _BodySchema(BaseModel):
    recipient_owner_id: IdSchema


class _ResponseSchema(BaseModel):
    content: str


class GenerateIcebreakerController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/icebreaker',
            status_code=HTTPStatus.CREATED,
            response_model=_ResponseSchema,
        )
        def _(
            body: _BodySchema,
            owner_id: Id = Depends(ProfilingPipe.get_owner_id),
            workflow: GenerateIcebreakerWorkflow = Depends(
                AiPipe.get_generate_icebreaker_workflow_from_request
            ),
        ) -> _ResponseSchema:
            icebreaker = workflow.run(
                sender_id=owner_id.value,
                recipient_id=body.recipient_owner_id,
            )
            return _ResponseSchema(content=icebreaker)
