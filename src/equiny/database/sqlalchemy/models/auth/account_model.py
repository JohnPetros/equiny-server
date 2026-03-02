from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from equiny.database.sqlalchemy.models.model import Model

if TYPE_CHECKING:
    from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel


class AccountModel(Model):
    __tablename__ = 'accounts'

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    password: Mapped[str]
    is_verified: Mapped[bool] = mapped_column(default=False)

    owners: Mapped[list['OwnerModel']] = relationship(
        back_populates='account',
        cascade='all, delete-orphan',
    )
