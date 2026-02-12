from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.core.auth.interfaces.providers.hash_provider import HashProvider
from equiny.core.auth.interfaces.providers.jwt_provider import JwtProvider
from equiny.core.auth.interfaces.repositories import AccountsRepository
from equiny.core.shared.interfaces import Broker
from equiny.core.auth.domain.events import AccountCreatedEvent


class SignUpAccountUseCase:
    def __init__(
        self,
        hash_provider: HashProvider,
        jwt_provider: JwtProvider,
        repository: AccountsRepository,
        broker: Broker,
    ) -> None:
        self.hash_provider = hash_provider
        self.jwt_provider = jwt_provider
        self.repository = repository
        self.broker = broker

    def execute(
        self,
        account_email: str,
        account_password: str,
        owner_name: str,
    ) -> AccountDto:
        hashed_password = self.hash_provider.generate(account_password)
        account = Account.create(
            AccountDto(email=account_email, password=hashed_password)
        )
        self.repository.add(account)
        self.broker.publish(
            AccountCreatedEvent(account_id=account.id.value, owner_name=owner_name)
        )
        return account.dto
