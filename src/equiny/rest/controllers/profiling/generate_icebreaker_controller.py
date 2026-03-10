from http import HTTPStatus

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from equiny.core.conversation.interfaces import GenerateIcebreakerWorkflow
from equiny.pipes.ai_pipe import AiPipe
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.matching_pipe import MatchingPipe
from equiny.validation.shared.id_schema import IdSchema


class _BodySchema(BaseModel):
    sender_horse_id: IdSchema
    recipient_horse_id: IdSchema


class GenerateIcebreakerController:
    @staticmethod
    def handle(router: APIRouter) -> None:
        @router.post(
            '/icebreaker',
            status_code=HTTPStatus.ACCEPTED,
            dependencies=[
                Depends(AuthPipe.verify_jwt),
                Depends(MatchingPipe.verify_match),
            ],
        )
        def _(
            body: _BodySchema,
            workflow: GenerateIcebreakerWorkflow = Depends(
                AiPipe.get_generate_icebreaker_workflow_from_request
            ),
        ) -> None:
            workflow.run(
                sender_horse_id=body.sender_horse_id,
                recipient_horse_id=body.recipient_horse_id,
            )
