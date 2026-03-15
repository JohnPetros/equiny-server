from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from equiny.database.sqlalchemy.models.model import Model

if TYPE_CHECKING:
    from equiny.database.sqlalchemy.models.auth.account_model import AccountModel


class SocialAccountModel(Model):
    __tablename__ = 'social_accounts'
    __table_args__ = (
        UniqueConstraint('account_id', 'provider'),
        UniqueConstraint('provider', 'email'),
    )

    id: Mapped[str] = mapped_column(primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id'), index=True)
    email: Mapped[str]
    provider: Mapped[str]

    account: Mapped['AccountModel'] = relationship(back_populates='social_accounts')
