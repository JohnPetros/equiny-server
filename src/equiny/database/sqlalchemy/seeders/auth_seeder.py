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
                email='mariana.duarte@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='rafael.monteiro@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='camila.nascimento@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='bruno.almeida@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='fernanda.ribeiro@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='lucas.ferreira@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='juliana.santos@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='tiago.oliveira@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='patricia.lima@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
            AccountsFaker.fake(
                email='gustavo.barros@equiny.dev',
                password=self._hash_provider.generate('12345678'),
            ),
        ]

        self._accounts_repository.add_many(accounts)
        return [account.id for account in accounts]
