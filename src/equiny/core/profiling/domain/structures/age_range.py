from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.profiling.domain.structures.dtos.age_range_dto import AgeRangeDto
from equiny.core.shared.domain.structures.integer import Integer
from equiny.core.shared.domain.errors import ValidationError


@structure
class AgeRange(Structure):
    min_age: Integer
    max_age: Integer

    @staticmethod
    def create(dto: AgeRangeDto) -> 'AgeRange':
        if dto.min_age < 0 or dto.max_age > 30 or dto.min_age > 30 or dto.max_age < 0:
            raise ValidationError(
                f'A idade deve ser entre 0 e 30 anos, obtido {dto.min_age} e {dto.max_age}'
            )

        if dto.max_age < dto.min_age:
            raise ValidationError(
                f'A idade máxima deve ser maior que a idade mínima, obtido {dto.min_age} e {dto.max_age}'
            )

        return AgeRange(
            min_age=Integer.create(dto.min_age), max_age=Integer.create(dto.max_age)
        )
