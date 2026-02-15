from faker import Faker

from equiny.core.profiling.domain.entities.dtos import OwnerDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.fakers.shared.structures.id_faker import IdFaker


class OwnersFaker:
    _faker = Faker()

    @staticmethod
    def fake(
        name: str | None = None,
        email: str | None = None,
        account_id: str | None = None,
    ) -> Owner:
        return Owner.create(OwnersFaker.fake_dto(account_id=account_id, email=email))

    @staticmethod
    def fake_dto(
        name: str | None = None,
        email: str | None = None,
        account_id: str | None = None,
    ) -> OwnerDto:
        return OwnerDto(
            id=IdFaker.fake().value,
            name=name or OwnersFaker._faker.name(),
            email=email or OwnersFaker._faker.email(),
            account_id=account_id or IdFaker.fake().value,
        )
