from fastapi import Depends

from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.shared.domain.errors import NotFoundError
from equiny.core.shared.domain.structures.id import Id
from equiny.pipes.auth_pipe import AuthPipe
from equiny.pipes.database_pipe import DatabasePipe


class ProfilingPipe:
    @staticmethod
    def get_owner_id(
        jwt_payload: dict[str, str] = Depends(AuthPipe.verify_jwt),
        owners_repository: OwnersRepository = Depends(
            DatabasePipe.get_owners_repository
        ),
    ) -> Id:
        account_id = Id.create(jwt_payload['sub'])
        owner = owners_repository.find_by_account_id(account_id)
        if owner is None:
            raise NotFoundError('Owner não encontrado para a conta autenticada')
        return owner.id
