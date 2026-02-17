from ulid import ULID

from equiny.core.shared.domain.structures.id import Id


class IdFaker:
    @staticmethod
    def fake() -> Id:
        return Id.create(str(ULID()))
