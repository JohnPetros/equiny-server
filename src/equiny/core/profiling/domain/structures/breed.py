from enum import Enum

from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.errors import ValidationError


class BreedValue(Enum):
    QUARTO_DE_MILHA = 'quarto de milha'
    MANGALARGA_MARCHADOR = 'mangalarga marchador'
    CRIOULO = 'criolo'
    PURO_SANGUE_INGLES = 'puro sangue inglês'
    ARABE = 'arabe'
    CAMPOLINA = 'campolina'
    OUTRA = 'outra'


@structure
class Breed(Structure):
    value: BreedValue

    @classmethod
    def create(cls, value: str) -> 'Breed':
        try:
            return cls(BreedValue(value))
        except ValueError as error:
            raise ValidationError(f'Raca invalida: {value}') from error

    @classmethod
    def create_as_arabe(cls) -> 'Breed':
        return cls(BreedValue.ARABE)

    @property
    def is_arabe(self) -> bool:
        return self.value == BreedValue.ARABE

    @property
    def is_criolo(self) -> bool:
        return self.value == BreedValue.CRIOULO

    @property
    def is_puro_sangue_ingles(self) -> bool:
        return self.value == BreedValue.PURO_SANGUE_INGLES

    @property
    def is_quarto_de_milha(self) -> bool:
        return self.value == BreedValue.QUARTO_DE_MILHA

    @property
    def is_mangalarga_marchador(self) -> bool:
        return self.value == BreedValue.MANGALARGA_MARCHADOR

    @property
    def dto(self) -> str:
        return self.value.value
