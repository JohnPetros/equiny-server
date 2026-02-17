from equiny.core.auth.interfaces.repositories.accounts_repository import (
    AccountsRepository,
)
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.fakers.auth.entities import AccountsFaker
from equiny.core.shared.domain.structures.id import Id


class AuthSeeder:
    def __init__(
        self, accounts_repository: AccountsRepository, hash_provider: HashProvider
    ) -> None:
        self._accounts_repository = accounts_repository
        self._hash_provider = hash_provider

    def seed(self) -> list[Id]:
        accounts = [
            AccountsFaker.fake(
                email='petros@equiny.com',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='vitor@equiny.com',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='renato@equiny.com',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='paulo@equiny.com',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='ricardo@equiny.com',
                password=self._hash_provider.generate('12345678'),
            ),
        ]

        self._accounts_repository.add_many(accounts)
        return [account.id for account in accounts]
