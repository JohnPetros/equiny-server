from faker import Faker

from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.fakers.shared.structures.id_faker import IdFaker


class AccountsFaker:
    _faker = Faker()

    @staticmethod
    def fake(
        account_id: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> Account:
        return Account.create(AccountsFaker.fake_dto(account_id, email, password))

    @staticmethod
    def fake_dto(
        account_id: str | None = None,
        email: str | None = None,
        password: str | None = None,
    ) -> AccountDto:
        return AccountDto(
            id=account_id or IdFaker.fake().value,
            email=email or AccountsFaker._faker.email(),
            password=password or AccountsFaker._faker.password(),
        )

    @staticmethod
    def fake_many(count: int) -> list[Account]:
        return [AccountsFaker.fake() for _ in range(count)]

    @staticmethod
    def fake_many_dto(count: int) -> list[AccountDto]:
        return [AccountsFaker.fake_dto() for _ in range(count)]
