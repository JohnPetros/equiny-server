from equiny.core.shared.domain.decorators.dto import dto


@dto
class AgeRangeDto:
    min_age: int
    max_age: int
