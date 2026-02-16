from enum import Enum

from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.errors import ValidationError


class SexValue(Enum):
    MALE = 'male'
    FEMALE = 'female'


@structure
class Sex(Structure):
    value: SexValue

    @classmethod
    def create(cls, value: str) -> 'Sex':
        match value:
            case SexValue.MALE.value:
                return cls.create_as_male()
            case SexValue.FEMALE.value:
                return cls.create_as_female()
            case _:
                raise ValidationError(f'Sexo inválido: {value}')

    @classmethod
    def create_as_male(cls) -> 'Sex':
        return cls(SexValue.MALE)

    @classmethod
    def create_as_female(cls) -> 'Sex':
        return cls(SexValue.FEMALE)

    @property
    def dto(self) -> str:
        return self.value.value
