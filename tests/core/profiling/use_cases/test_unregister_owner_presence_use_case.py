import pytest
from unittest.mock import Mock, create_autospec

from equiny.constants import CACHE_KEYS
from equiny.core.profiling.domain.errors.owner_not_found_error import OwnerNotFoundError
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.use_cases.unregister_owner_presence_use_case import (
    UnregisterOwnerPresenceUseCase,
)
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from tests.fakers.profiling.entities.owners_faker import OwnersFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestUnregisterOwnerPresenceUseCase:
    cache_provider_mock: Mock
    repository_mock: Mock
    use_case: UnregisterOwnerPresenceUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.cache_provider_mock = create_autospec(CacheProvider, instance=True)
        self.repository_mock = create_autospec(OwnersRepository, instance=True)
        self.use_case = UnregisterOwnerPresenceUseCase(
            cache_provider=self.cache_provider_mock,
            repository=self.repository_mock,
        )

    def test_should_delete_cache_key_and_replace_owner_when_owner_exists(self) -> None:
        owner = OwnersFaker.fake()
        self.repository_mock.find_by_id.return_value = owner

        self.use_case.execute(owner_id=owner.id.value)

        expected_cache_key = f'{CACHE_KEYS.OWNERS_PRESENCE}:{owner.id.value}'
        self.cache_provider_mock.delete.assert_called_once_with(expected_cache_key)
        self.repository_mock.find_by_id.assert_called_once()
        self.repository_mock.replace.assert_called_once()
        replaced_owner = self.repository_mock.replace.call_args[0][0]
        assert replaced_owner.id == owner.id
        assert replaced_owner.last_presence_at is not None

    def test_should_raise_owner_not_found_error_when_owner_does_not_exist(self) -> None:
        owner_id = IdFaker.fake().value
        self.repository_mock.find_by_id.return_value = None

        with pytest.raises(OwnerNotFoundError):
            self.use_case.execute(owner_id=owner_id)

        self.repository_mock.find_by_id.assert_called_once()
        self.repository_mock.replace.assert_not_called()
