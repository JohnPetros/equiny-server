from __future__ import annotations

from typing import TYPE_CHECKING

from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.database.sqlalchemy.repositories.auth import SqlalchemyAccountsRepository
from equiny.database.sqlalchemy.repositories.profiling import (
    SqlalchemyHorsesRepository,
    SqlalchemyOwnersRepository,
)
from equiny.database.sqlalchemy.sqlalchemy import Sqlalchemy
from equiny.providers.hash import PwdlibHashProvider
from faker import Faker

from equiny.fakers.profiling.entities.horses_faker import HorsesFaker
from equiny.fakers.profiling.entities.owners_faker import OwnersFaker

if TYPE_CHECKING:
    from equiny.core.auth.interfaces.repositories.accounts_repository import (
        AccountsRepository,
    )
    from equiny.core.profiling.interfaces.repositories import OwnersRepository


TEST_ACCOUNT_EMAIL = 'test@equiny.com'
TEST_ACCOUNT_PASSWORD = '123456'  # noqa: S105

SEED_EXTRA_OWNERS_COUNT = 4


def seed() -> None:
    from sqlalchemy import delete

    from equiny.database.sqlalchemy.models.auth import AccountModel
    from equiny.database.sqlalchemy.models.profiling import (
        HorseImageModel,
        HorseModel,
        OwnerModel,
    )

    _ = (AccountModel, OwnerModel, HorseModel, HorseImageModel)

    session = Sqlalchemy.get_session()
    try:
        session.execute(delete(HorseImageModel))
        session.execute(delete(HorseModel))
        session.execute(delete(OwnerModel))
        session.execute(delete(AccountModel))
        session.commit()

        hash_provider = PwdlibHashProvider()
        account_repository: AccountsRepository = SqlalchemyAccountsRepository(session)
        owners_repository: OwnersRepository = SqlalchemyOwnersRepository(session)
        horses_repository = SqlalchemyHorsesRepository(session)

        hashed_password = hash_provider.generate(TEST_ACCOUNT_PASSWORD)
        account = Account.create(
            AccountDto(email=TEST_ACCOUNT_EMAIL, password=hashed_password)
        )
        account_repository.add(account)

        owner = OwnersFaker.fake(
            account_id=account.id.value,
            email=account.email.value,
            has_completed_onboarding=False,
        )
        owners_repository.add(owner)

        horse = HorsesFaker.fake()
        horses_repository.add(horse, owner_id=owner.id)

        faker = Faker()
        for _ in range(SEED_EXTRA_OWNERS_COUNT):
            extra_email = faker.unique.email()
            extra_password = hash_provider.generate('123456')
            extra_account = Account.create(
                AccountDto(email=extra_email, password=extra_password)
            )
            account_repository.add(extra_account)

            extra_owner = OwnersFaker.fake(
                account_id=extra_account.id.value,
                email=extra_account.email.value,
            )
            owners_repository.add(extra_owner)

            extra_horse = HorsesFaker.fake()
            horses_repository.add(extra_horse, owner_id=extra_owner.id)

        session.commit()
    finally:
        session.close()
