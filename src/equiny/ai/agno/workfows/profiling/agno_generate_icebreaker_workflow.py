from typing import TYPE_CHECKING, cast

from agno.run.base import RunContext
from agno.workflow import Parallel, Step, StepInput, StepOutput, Workflow
from equiny.ai.agno.tookits import ProfilingToolkit
from equiny.core.conversation.interfaces import GenerateIcebreakerWorkflow
from equiny.core.conversation.use_cases import SendIcebreakerUseCase
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.shared.domain.errors.app_error import AppError
from equiny.core.shared.interfaces.broker import Broker

if TYPE_CHECKING:
    from agno.workflow.step import StepExecutor


class AgnoGenerateIcebreakerWorkflow(GenerateIcebreakerWorkflow):
    def __init__(self, repository: HorsesRepository, broker: Broker) -> None:
        self._repository = repository
        self._broker = broker

    def run(self, sender_horse_id: str, recipient_horse_id: str) -> None:
        workflow = Workflow(
            name='generate-icebreaker',
            description='Generate an icebreaker for a conversation',
            steps=[
                Parallel(
                    Step(  # pyright: ignore[reportArgumentType]
                        name='get-sender-horse',
                        description='Get the sender horse',
                        executor=cast(
                            'StepExecutor',
                            self._get_sender_horse_step,
                        ),
                    ),
                    Step(  # pyright: ignore[reportArgumentType]
                        name='get-recipient-horse',
                        description='Get the recipient horse',
                        executor=cast(
                            'StepExecutor',
                            self._get_recipient_horse_step,
                        ),
                    ),
                    name='fetch-horses',
                    description='Fetch sender and recipient horses',
                ),
                Step(
                    name='generate-icebreaker',
                    description='Generate an icebreaker for a conversation',
                    executor=cast(
                        'StepExecutor',
                        self._generate_icebreaker_step,
                    ),
                ),
                Step(
                    name='send-icebreaker',
                    description='Send an icebreaker to a recipient',
                    executor=cast(
                        'StepExecutor',
                        self._send_icebreaker_step,
                    ),
                ),
            ],
            session_state={
                'sender_horse_id': sender_horse_id,
                'recipient_horse_id': recipient_horse_id,
            },
        )

        workflow.run(input='start')

    def _get_sender_horse_step(
        self, _: StepInput, run_context: RunContext
    ) -> StepOutput:
        if run_context.session_state is None:
            raise AppError('Session state is required', 'Session state is required')

        sender_horse_id = str(run_context.session_state.get('sender_horse_id'))

        toolkit = ProfilingToolkit(self._repository)
        result = toolkit.get_horse_tool(sender_horse_id)

        return StepOutput(content=result)

    def _get_recipient_horse_step(
        self, _: StepInput, run_context: RunContext
    ) -> StepOutput:
        if run_context.session_state is None:
            raise AppError('Session state is required', 'Session state is required')

        recipient_horse_id = str(run_context.session_state.get('recipient_horse_id'))

        toolkit = ProfilingToolkit(self._repository)
        result = toolkit.get_horse_tool(recipient_horse_id)

        return StepOutput(content=result)

    def _generate_icebreaker_step(self, step_input: StepInput) -> StepOutput:
        sender_horse = step_input.get_step_content('get-sender-horse')
        recipient_horse = step_input.get_step_content('get-recipient-horse')

        icebreaker = f"""
        Sender: {sender_horse}
        Recipient: {recipient_horse}
        """

        return StepOutput(content=icebreaker)

    def _send_icebreaker_step(
        self, step_input: StepInput, run_context: RunContext
    ) -> StepOutput:
        if run_context.session_state is None:
            raise AppError('Session state is required', 'Session state is required')

        sender_horse_id = str(run_context.session_state.get('sender_horse_id'))
        recipient_horse_id = str(run_context.session_state.get('recipient_horse_id'))
        icebreaker = str(step_input.get_step_content('generate-icebreaker'))

        use_case = SendIcebreakerUseCase(self._repository, self._broker)
        use_case.execute(
            sender_horse_id=sender_horse_id,
            recipient_horse_id=recipient_horse_id,
            icebreaker=icebreaker,
        )

        return StepOutput(content=icebreaker)
