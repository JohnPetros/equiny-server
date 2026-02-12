from sqlalchemy.orm import Mapped, mapped_column
from equiny.database.sqlalchemy.models.model import Model


class OwnerModel(Model):
    __tablename__ = 'owners'

    id: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str]
    account_id: Mapped[str]
