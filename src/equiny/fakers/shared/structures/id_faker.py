from faker import Faker

from equiny.core.shared.domain.structures.id import Id


class IdFaker:
    _faker = Faker()

    @staticmethod
    def fake() -> Id:
        return Id.create(IdFaker._faker.uuid4())
