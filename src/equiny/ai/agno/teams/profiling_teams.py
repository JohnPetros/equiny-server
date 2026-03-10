from agno.agent import Agent


class ProfilingTeam:
    @property
    def icebreaker_agent(self) -> Agent:

        return Agent(
            name='Icebreaker Agent',
            description='An agent that generates icebreakers for conversations',
        )
