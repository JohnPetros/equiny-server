from datetime import datetime
from equiny.core.shared.domain.decorators import structure
from equiny.core.shared.domain.abstracts import Structure


@structure
class Datetime(Structure):
    value: datetime

    @classmethod
    def create(cls, datetime: datetime) -> 'Datetime':
        return Datetime(value=datetime)
