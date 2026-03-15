from enum import Enum

from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts.structure import Structure
from equiny.core.shared.domain.errors.validation_error import ValidationError


class SocialAccountProviderValue(Enum):
    GOOGLE = 'google'


@structure
class SocialAccountProvider(Structure):
    value: SocialAccountProviderValue

    @classmethod
    def create(cls, value: str) -> 'SocialAccountProvider':
        try:
            return cls(SocialAccountProviderValue(value))
        except ValueError as error:
            raise ValidationError(
                f'Social account provider invalid: {value}'
            ) from error

    @property
    def dto(self) -> str:
        return self.value.value
