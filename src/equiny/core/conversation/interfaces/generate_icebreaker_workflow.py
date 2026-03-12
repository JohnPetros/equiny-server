from typing import Protocol


class GenerateIcebreakerWorkflow(Protocol):
    def run(self, sender_id: str, recipient_id: str) -> str: ...
