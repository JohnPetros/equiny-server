from unittest.mock import Mock, create_autospec

import pytest

from src.equiny.core.profiling.interfaces.repositories import HorsesRepository
from src.equiny.core.profiling.use_cases.get_owner_horses_use_case import (
    GetOwnerHorsesUseCase,
)
from src.equiny.core.shared.domain.errors import ValidationError
from tests.fakers.profiling.entities.horses_faker import HorsesFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestGetOwnerHorsesUseCase:
    repository_mock: Mock
    use_case: GetOwnerHorsesUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(HorsesRepository, instance=True)
        self.use_case = GetOwnerHorsesUseCase(repository=self.repository_mock)

    def test_should_return_owner_horses_dto_when_owner_has_horses(self) -> None:
        owner_id = IdFaker.fake().value
        horses = HorsesFaker.fake_many(count=2)
        self.repository_mock.find_many_by_owner.return_value = horses

        result = self.use_case.execute(owner_id=owner_id)

        self.repository_mock.find_many_by_owner.assert_called_once()
        searched_owner_id = self.repository_mock.find_many_by_owner.call_args[0][0]
        assert searched_owner_id.value == owner_id
        assert result == [horse.dto for horse in horses]

    def test_should_raise_validation_error_when_owner_id_is_invalid(self) -> None:
        invalid_owner_id = '6fa459ea-ee8a-11d2-9901-001045409ca1'

        with pytest.raises(ValidationError):
            self.use_case.execute(owner_id=invalid_owner_id)

        self.repository_mock.find_many_by_owner.assert_not_called()
