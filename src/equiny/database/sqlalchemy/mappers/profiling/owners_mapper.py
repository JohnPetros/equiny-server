from equiny.core.profiling.domain.entities.dtos.owner_dto import OwnerDto
from equiny.core.profiling.domain.entities.owner import Owner
from equiny.database.sqlalchemy.models.profiling.owner_model import OwnerModel


class OwnersMapper:
    @staticmethod
    def to_entity(owner_model: OwnerModel) -> Owner:
        return Owner.create(OwnersMapper.to_dto(owner_model))

    @staticmethod
    def to_dto(owner_model: OwnerModel) -> OwnerDto:
        return OwnerDto(
            id=owner_model.id,
            name=owner_model.name,
            email=owner_model.email,
            account_id=owner_model.account_id,
            has_completed_onboarding=False,
        )

    @staticmethod
    def to_model(owner: Owner) -> OwnerModel:
        return OwnerModel(
            id=owner.id.value,
            name=owner.name.value,
            email=owner.email.value,
            account_id=owner.account_id.value,
            has_completed_onboarding=owner.has_completed_onboarding.value,
        )
