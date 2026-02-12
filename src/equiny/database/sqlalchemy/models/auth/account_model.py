from sqlalchemy.orm import Mapped, mapped_column

from equiny.database.sqlalchemy.models.model import Model


class AccountModel(Model):
    __tablename__ = 'accounts'

    id: Mapped[str] = mapped_column(primary_key=True)
    email: Mapped[str]
    password: Mapped[str]
