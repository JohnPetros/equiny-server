from __future__ import annotations

from typing import TYPE_CHECKING

from equiny.core.auth.domain.entities.account import Account
from equiny.core.auth.domain.entities.dtos.account_dto import AccountDto
from equiny.database.sqlalchemy.repositories.auth import SqlalchemyAccountsRepository
from equiny.database.sqlalchemy.sqlalchemy import Sqlalchemy
from equiny.providers.hash import PwdlibHashProvider

if TYPE_CHECKING:
    from equiny.core.auth.interfaces.repositories.accounts_repository import (
        AccountsRepository,
    )


TEST_ACCOUNT_EMAIL = 'test@equiny.com'
TEST_ACCOUNT_PASSWORD = '123456'  # noqa: S105


def seed() -> None:
    from equiny.database.sqlalchemy.models.auth import AccountModel
    from equiny.database.sqlalchemy.models.profiling import OwnerModel

    _ = (AccountModel, OwnerModel)  # Register models in SQLAlchemy metadata

    session = Sqlalchemy.get_session()
    try:
        hash_provider = PwdlibHashProvider()
        repository: AccountsRepository = SqlalchemyAccountsRepository(session)

        existing = repository.find_by_email(TEST_ACCOUNT_EMAIL)
        if existing is not None:
            return

        hashed_password = hash_provider.generate(TEST_ACCOUNT_PASSWORD)
        account = Account.create(
            AccountDto(email=TEST_ACCOUNT_EMAIL, password=hashed_password)
        )
        repository.add(account)
        session.commit()
    finally:
        session.close()
