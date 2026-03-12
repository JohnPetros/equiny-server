from textwrap import dedent

from agno.agent import Agent
from agno.models.google import Gemini


class ProfilingTeam:
    @property
    def icebreaker_agent(self) -> Agent:
        return Agent(
            name='Icebreaker Agent',
            description='An agent that generates icebreakers for conversations',
            instructions=dedent(
                """
                You are an expert in icebreaking conversations.
                You are given a sender and a recipient that are both horse owners that are interested in talking to each other. You need to generate an icebreaker in PT-BR for the sender.
                Avoid robotic responses and use a friendly and natural tone.
                Avoid line breaks and keep the message short.
                The icebreaker should be a short, engaging message that will help the sender and recipient connect based on their horses.
                """
            ),
            model=Gemini(id='gemini-2.5-flash'),
        )
