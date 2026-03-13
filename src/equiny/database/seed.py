from __future__ import annotations

from equiny.database.sqlalchemy.models.conversation.attachment_model import (
    AttachmentModel,
)
from equiny.database.sqlalchemy.models.conversation.chat_model import ChatModel
from equiny.database.sqlalchemy.repositories.auth import SqlalchemyAccountsRepository
from equiny.database.sqlalchemy.repositories.profiling import (
    SqlalchemyHorsesRepository,
    SqlalchemyOwnersRepository,
)
from equiny.database.sqlalchemy.repositories.matching import SqlalchemyMatchesRepository
from equiny.database.sqlalchemy.seeders.auth_seeder import AuthSeeder
from equiny.database.sqlalchemy.seeders.profiling_seeder import ProfilingSeeder
from equiny.database.sqlalchemy.seeders.storage_seeder import StorageSeeder
from equiny.database.sqlalchemy.seeders.matching_seeder import MatchingSeeder
from equiny.database.sqlalchemy.sqlalchemy import Sqlalchemy
from equiny.providers.hash import PwdlibHashProvider
from equiny.providers.storage.supabase.supabase_file_storage_provider import (
    SupabaseFileStorageProvider,
)
from equiny.database.sqlalchemy.models.conversation.message_model import MessageModel


def seed() -> None:
    from sqlalchemy import delete

    from equiny.database.sqlalchemy.models.auth import AccountModel
    from equiny.database.sqlalchemy.models.profiling import (
        HorseImageModel,
        HorseModel,
        OwnerModel,
    )
    from equiny.database.sqlalchemy.models.matching import MatchModel, SwipeModel

    _ = (AccountModel, OwnerModel, HorseModel, HorseImageModel)

    session = Sqlalchemy.get_session()
    try:
        session.execute(delete(HorseImageModel))
        session.execute(delete(AttachmentModel))
        session.execute(delete(MessageModel))
        session.execute(delete(ChatModel))
        session.execute(delete(SwipeModel))
        session.execute(delete(MatchModel))
        session.execute(delete(HorseModel))
        session.execute(delete(OwnerModel))
        session.execute(delete(AccountModel))
        session.commit()

        hash_provider = PwdlibHashProvider()
        file_storage_provider = SupabaseFileStorageProvider()
        account_repository = SqlalchemyAccountsRepository(session)
        owners_repository = SqlalchemyOwnersRepository(session)
        horses_repository = SqlalchemyHorsesRepository(session)
        matches_repository = SqlalchemyMatchesRepository(session)

        auth_seeder = AuthSeeder(account_repository, hash_provider)
        profiling_seeder = ProfilingSeeder(horses_repository, owners_repository)
        storage_seeder = StorageSeeder(file_storage_provider)
        matching_seeder = MatchingSeeder(matches_repository)

        accounts_ids = auth_seeder.seed()
        horses_ids = profiling_seeder.seed(accounts_ids)
        session.commit()
        matching_seeder.seed(horses_ids)
        storage_seeder.seed()
        session.commit()
    finally:
        session.close()
