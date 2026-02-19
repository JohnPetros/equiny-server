from enum import Enum

from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.structures.logical import Logical


class SwipeDecisionValue(Enum):
    LIKE = 'like'
    DISLIKE = 'dislike'


@structure
class SwipeDecision(Structure):
    value: SwipeDecisionValue

    @classmethod
    def create(cls, value: str) -> 'SwipeDecision':
        return SwipeDecision(value=SwipeDecisionValue(value))

    def is_like(self) -> Logical:
        return Logical.create(self.value == SwipeDecisionValue.LIKE)

    def is_dislike(self) -> Logical:
        return Logical.create(self.value == SwipeDecisionValue.DISLIKE)

    @property
    def dto(self) -> str:
        return self.value.value
