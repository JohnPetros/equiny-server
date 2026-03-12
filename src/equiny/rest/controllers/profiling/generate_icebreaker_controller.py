from http import HTTPStatus

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from equiny.core.conversation.interfaces import GenerateIcebreakerWorkflow
from equiny.pipes.ai_pipe import AiPipe
from equiny.pipes.auth_pipe import AuthPipe
from equiny.validation.shared.id_schema import IdSchema


class _BodySchema(BaseModel):
    sender_id: IdSchema
    recipient_id: IdSchema


class _ResponseSchema(BaseModel):
    content: str


class GenerateIcebreakerController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/icebreaker',
            status_code=HTTPStatus.CREATED,
            response_model=_ResponseSchema,
            dependencies=[
                Depends(AuthPipe.verify_jwt),
            ],
        )
        def _(
            body: _BodySchema,
            workflow: GenerateIcebreakerWorkflow = Depends(
                AiPipe.get_generate_icebreaker_workflow_from_request
            ),
        ) -> _ResponseSchema:
            icebreaker = workflow.run(
                sender_id=body.sender_id,
                recipient_id=body.recipient_id,
            )
            return _ResponseSchema(content=icebreaker)
