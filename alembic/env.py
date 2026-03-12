import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from pydantic_settings import BaseSettings, SettingsConfigDict

from alembic import context

from equiny.database.sqlalchemy.models.auth.account_model import AccountModel
from equiny.database.sqlalchemy.models.matching.match_model import MatchModel
from equiny.database.sqlalchemy.models.matching.swipe_model import SwipeModel
from equiny.database.sqlalchemy.models.conversation.attachment_model import (
    AttachmentModel,
)
from equiny.database.sqlalchemy.models.conversation.chat_model import ChatModel
from equiny.database.sqlalchemy.models.conversation.message_model import MessageModel
from equiny.database.sqlalchemy.models.model import Model
from equiny.database.sqlalchemy.models.profiling.horse_model import HorseModel
from equiny.database.sqlalchemy.models.profiling.horse_image_model import (
    HorseImageModel,
)
from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Model.metadata

# Import all models so they are registered in metadata.
_ = AccountModel
_ = HorseModel
_ = HorseImageModel
_ = OwnerModel
_ = SwipeModel
_ = MatchModel
_ = ChatModel
_ = MessageModel
_ = AttachmentModel


class AlembicEnv(BaseSettings):
    DATABASE_URL: str | None = None

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


database_url = os.getenv('DATABASE_URL') or AlembicEnv().DATABASE_URL

if database_url and database_url.startswith('postgresql://'):
    database_url = database_url.replace('postgresql://', 'postgresql+psycopg://', 1)

if database_url:
    config.set_main_option('sqlalchemy.url', database_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option('sqlalchemy.url') or ''
    is_sqlite = url.startswith('sqlite')

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
        render_as_batch=is_sqlite,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix='sqlalchemy.',
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=connection.dialect.name == 'sqlite',
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
