from typing import TYPE_CHECKING, NamedTuple, cast

from agno.run.base import RunContext
from agno.workflow import Parallel, Step, StepInput, StepOutput, Workflow
from equiny.ai.agno.teams.profiling_teams import ProfilingTeam
from equiny.ai.agno.toolkits import ProfilingToolkit
from equiny.core.conversation.interfaces import GenerateIcebreakerWorkflow
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.domain.errors.app_error import AppError
from equiny.core.shared.domain.structures.id import Id

if TYPE_CHECKING:
    from agno.workflow.step import StepExecutor


class _StepNames(NamedTuple):
    GET_SENDER_HORSE: str = 'get-sender-horse'
    GET_RECIPIENT_HORSE: str = 'get-recipient-horse'
    GET_COMMON_MATCHES: str = 'get-common-horse-matches'
    GENERATE_ICEBREAKER: str = 'generate-icebreaker'
    SEND_ICEBREAKER: str = 'send-icebreaker'


class AgnoGenerateIcebreakerWorkflow(GenerateIcebreakerWorkflow):
    def __init__(self, repository: HorsesRepository) -> None:
        self._repository = repository
        self._team = ProfilingTeam()
        self._step_names = _StepNames()

    def run(self, sender_id: str, recipient_id: str) -> str:
        workflow = Workflow(
            name='generate-icebreaker',
            description='Generate an icebreaker for a conversation',
            steps=[
                Parallel(
                    Step(  # pyright: ignore[reportArgumentType]
                        name=self._step_names.GET_SENDER_HORSE,
                        description='Get the sender horse',
                        executor=cast(
                            'StepExecutor',
                            self._get_sender_horse_step,
                        ),
                    ),
                    Step(  # pyright: ignore[reportArgumentType]
                        name=self._step_names.GET_RECIPIENT_HORSE,
                        description='Get the recipient horse',
                        executor=cast(
                            'StepExecutor',
                            self._get_recipient_horse_step,
                        ),
                    ),
                    Step(  # pyright: ignore[reportArgumentType]
                        name=self._step_names.GET_COMMON_MATCHES,
                        description='Get horse matches in common for both owners',
                        executor=cast(
                            'StepExecutor',
                            self._get_common_horse_matches_step,
                        ),
                    ),
                    name='fetch-horses',
                    description='Fetch sender and recipient horses',
                ),
                Step(
                    name=self._step_names.GENERATE_ICEBREAKER,
                    description='Generate an icebreaker for a conversation',
                    agent=self._team.icebreaker_agent,
                ),
            ],
            session_state={
                'sender_owner_id': sender_id,
                'recipient_owner_id': recipient_id,
            },
        )

        output = workflow.run(input='start')
        return str(output.content)

    def _get_sender_horse_step(
        self, _: StepInput, run_context: RunContext
    ) -> StepOutput:
        if run_context.session_state is None:
            raise AppError('Session state is required', 'Session state is required')

        sender_owner_id = str(run_context.session_state.get('sender_owner_id'))
        sender_horse_id = self._resolve_primary_horse_id(sender_owner_id)

        toolkit = ProfilingToolkit(self._repository)
        result = toolkit.get_horse_tool(sender_horse_id)

        return StepOutput(content=result)

    def _get_recipient_horse_step(
        self, _: StepInput, run_context: RunContext
    ) -> StepOutput:
        if run_context.session_state is None:
            raise AppError('Session state is required', 'Session state is required')

        recipient_owner_id = str(run_context.session_state.get('recipient_owner_id'))
        recipient_horse_id = self._resolve_primary_horse_id(recipient_owner_id)

        toolkit = ProfilingToolkit(self._repository)
        result = toolkit.get_horse_tool(recipient_horse_id)

        return StepOutput(content=result)

    def _get_common_horse_matches_step(
        self, _: StepInput, run_context: RunContext
    ) -> StepOutput:
        if run_context.session_state is None:
            raise AppError('Session state is required', 'Session state is required')

        sender_owner_id = str(run_context.session_state.get('sender_owner_id'))
        recipient_owner_id = str(run_context.session_state.get('recipient_owner_id'))

        sender_matches = self._repository.find_horse_matches_by_owner_id(
            Id.create(sender_owner_id)
        )
        recipient_matches = self._repository.find_horse_matches_by_owner_id(
            Id.create(recipient_owner_id)
        )

        common_context = {
            'sender_to_recipient_matches': [
                match.dto
                for match in sender_matches
                if match.owner_id.value == recipient_owner_id
            ],
            'recipient_to_sender_matches': [
                match.dto
                for match in recipient_matches
                if match.owner_id.value == sender_owner_id
            ],
        }

        return StepOutput(content=common_context)

    def _resolve_primary_horse_id(self, owner_id: str) -> str:
        horses = self._repository.find_many_by_owner(Id.create(owner_id))
        if not horses:
            raise AppError('Horse not found', 'Horse not found')

        return min(horses, key=lambda horse: horse.id.value).id.value
