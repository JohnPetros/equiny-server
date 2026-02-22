from equiny.core.profiling.domain.entities.owner import Owner
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.shared.domain.structures.id import Id
from equiny.core.shared.domain.structures.logical import Logical
from equiny.database.sqlalchemy.mappers.profiling.owners_mapper import OwnersMapper
from equiny.database.sqlalchemy.repositories.sqlalchemy_repository import (
    SqlalchemyRepository,
)
from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel


class SqlalchemyOwnersRepository(SqlalchemyRepository, OwnersRepository):
    def add(self, owner: Owner) -> None:
        owner_model = OwnersMapper.to_model(owner)
        self.sqlalchemy.add(owner_model)

    def add_many(self, owners: list[Owner]) -> None:
        owner_models = [OwnersMapper.to_model(owner) for owner in owners]
        self.sqlalchemy.add_all(owner_models)

    def find_by_id(self, owner_id: Id) -> Owner | None:
        owner_model = (
            self.sqlalchemy.query(OwnerModel)
            .filter(OwnerModel.id == owner_id.value)
            .first()
        )
        if owner_model is None:
            return None
        return OwnersMapper.to_entity(owner_model)

    def find_all(self) -> list[Owner]:
        owner_models = self.sqlalchemy.query(OwnerModel).all()
        return [OwnersMapper.to_entity(owner_model) for owner_model in owner_models]

    def find_by_account_id(self, account_id: Id) -> Owner | None:
        owner_model = (
            self.sqlalchemy.query(OwnerModel)
            .filter(OwnerModel.account_id == account_id.value)
            .first()
        )
        if owner_model is None:
            return None
        return OwnersMapper.to_entity(owner_model)

    def replace(self, owner: Owner) -> None:
        owner_model = (
            self.sqlalchemy.query(OwnerModel)
            .filter(OwnerModel.id == owner.id.value)
            .first()
        )
        if owner_model is None:
            return

        owner_dto = owner.dto
        owner_model.name = owner_dto.name
        owner_model.email = owner_dto.email
        owner_model.account_id = owner_dto.account_id
        owner_model.bio = owner_dto.bio
        owner_model.phone = owner_dto.phone
        owner_model.avatar_key = (
            owner_dto.avatar.key if owner_dto.avatar is not None else None
        )
        owner_model.avatar_name = (
            owner_dto.avatar.name if owner_dto.avatar is not None else None
        )
        owner_model.has_completed_onboarding = owner_dto.has_completed_onboarding
        owner_model.last_presence_at = owner_dto.last_presence_at

    def update_has_completed_onboarding(
        self,
        owner_id: Id,
        has_completed_onboarding: Logical,
    ) -> None:
        owner_model = (
            self.sqlalchemy.query(OwnerModel)
            .filter(OwnerModel.id == owner_id.value)
            .first()
        )

        if owner_model is None:
            return

        owner_model.has_completed_onboarding = has_completed_onboarding.value
