from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.errors.validation_error import ValidationError


@structure
class Integer(Structure):
    value: int

    @classmethod
    def create(cls, value: int) -> 'Integer':
        if value < 0:
            raise ValidationError(f'Value must be greater than 0, got {value}')

        return cls(value)
