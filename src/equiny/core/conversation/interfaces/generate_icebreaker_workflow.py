from typing import Protocol


class GenerateIcebreakerWorkflow(Protocol):
    def run(self, sender_horse_id: str, recipient_horse_id: str) -> None: ...
