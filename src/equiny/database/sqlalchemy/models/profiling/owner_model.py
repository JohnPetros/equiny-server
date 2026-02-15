from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from equiny.database.sqlalchemy.models.model import Model

if TYPE_CHECKING:
    from equiny.database.sqlalchemy.models.auth.account_model import AccountModel
    from equiny.database.sqlalchemy.models.profiling.horse_model import HorseModel


class OwnerModel(Model):
    __tablename__ = 'owners'

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id'))

    account: Mapped['AccountModel'] = relationship(back_populates='owners')
    horses: Mapped[list['HorseModel']] = relationship(back_populates='owner')
