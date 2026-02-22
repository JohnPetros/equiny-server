import pytest
from unittest.mock import Mock, create_autospec

from equiny.constants import CACHE_KEYS
from equiny.core.profiling.domain.errors.owner_not_found_error import OwnerNotFoundError
from equiny.core.profiling.domain.structures.dtos.owner_presence_dto import (
    OwnerPresenceDto,
)
from equiny.core.profiling.interfaces.repositories import OwnersRepository
from equiny.core.profiling.use_cases.get_owner_presence_use_case import (
    GetOwnerPresenceUseCase,
)
from equiny.core.shared.interfaces.cache_provider import CacheProvider
from tests.fakers.profiling.entities.owners_faker import OwnersFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestGetOwnerPresenceUseCase:
    cache_provider_mock: Mock
    repository_mock: Mock
    use_case: GetOwnerPresenceUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.cache_provider_mock = create_autospec(CacheProvider, instance=True)
        self.repository_mock = create_autospec(OwnersRepository, instance=True)
        self.use_case = GetOwnerPresenceUseCase(
            cache_provider=self.cache_provider_mock,
            repository=self.repository_mock,
        )

    def test_should_return_owner_presence_dto_with_online_true_when_cache_key_exists(
        self,
    ) -> None:
        owner = OwnersFaker.fake()
        self.repository_mock.find_by_id.return_value = owner
        self.cache_provider_mock.get.return_value = owner.id.value

        result = self.use_case.execute(owner_id=owner.id.value)

        self.repository_mock.find_by_id.assert_called_once()
        expected_cache_key = f'{CACHE_KEYS.OWNERS_PRESENCE}:{owner.id.value}'
        self.cache_provider_mock.get.assert_called_once_with(expected_cache_key)
        assert isinstance(result, OwnerPresenceDto)
        assert result.owner_id == owner.id.value
        assert result.is_online is True

    def test_should_return_owner_presence_dto_with_online_false_when_cache_key_does_not_exist(
        self,
    ) -> None:
        owner = OwnersFaker.fake()
        self.repository_mock.find_by_id.return_value = owner
        self.cache_provider_mock.get.return_value = None

        result = self.use_case.execute(owner_id=owner.id.value)

        self.repository_mock.find_by_id.assert_called_once()
        expected_cache_key = f'{CACHE_KEYS.OWNERS_PRESENCE}:{owner.id.value}'
        self.cache_provider_mock.get.assert_called_once_with(expected_cache_key)
        assert isinstance(result, OwnerPresenceDto)
        assert result.owner_id == owner.id.value
        assert result.is_online is False

    def test_should_raise_owner_not_found_error_when_owner_does_not_exist(self) -> None:
        owner_id = IdFaker.fake().value
        self.repository_mock.find_by_id.return_value = None

        with pytest.raises(OwnerNotFoundError):
            self.use_case.execute(owner_id=owner_id)

        self.repository_mock.find_by_id.assert_called_once()
        self.cache_provider_mock.get.assert_not_called()
