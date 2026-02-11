from datetime import datetime
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure
from equiny.core.shared.domain.errors import ValidationError


@structure
class HorseBirth(Structure):
    month: int
    year: int

    @staticmethod
    def create(month: int, year: int) -> 'HorseBirth':
        if month < 1 or month > 12:
            raise ValidationError(f'Month must be between 1 and 12, got {month}')

        if year < 1900 or year > datetime.now().year:
            raise ValidationError(
                f'Year must be between 1900 and the current year, got {year}'
            )

        return HorseBirth(month=month, year=year)
