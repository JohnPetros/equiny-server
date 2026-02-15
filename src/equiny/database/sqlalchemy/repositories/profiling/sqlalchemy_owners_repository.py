from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.database.sqlalchemy.mappers.profiling.owners_mapper import OwnersMapper
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)
from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel


class SqlalchemyOwnersRepository(SqlalchemyRepository, OwnersRepository):
    def add(self, owner: Owner) -> None:
        owner_model = OwnersMapper.to_model(owner)
        self.sqlalchemy.add(owner_model)

    def find_by_id(self, owner_id: str) -> Owner | None:
        owner_model = (
            self.sqlalchemy.query(OwnerModel).filter(OwnerModel.id == owner_id).first()
        )
        if owner_model is None:
            return None
        return OwnersMapper.to_entity(owner_model)

    def find_by_account_id(self, account_id: str) -> Owner | None:
        owner_model = (
            self.sqlalchemy.query(OwnerModel)
            .filter(OwnerModel.account_id == account_id)
            .first()
        )
        if owner_model is None:
            return None
        return OwnersMapper.to_entity(owner_model)
