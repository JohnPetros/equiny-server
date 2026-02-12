import re

from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.errors import ValidationError


@structure
class Email(Structure):
    value: str

    @staticmethod
    def create(value: str) -> 'Email':
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', value):
            raise ValidationError(f'Invalid email address: {value}')
        return Email(value=value)
