from unittest.mock import Mock, create_autospec

import pytest

from equiny.core.profiling.domain.errors import HorseNotFoundError
from equiny.core.profiling.interfaces.repositories import HorsesRepository
from equiny.core.profiling.use_cases.toggle_horse_activation_use_case import (
    ToggleHorseActivationUseCase,
)
from tests.fakers.profiling.entities.horses_faker import HorsesFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestToggleHorseActivationUseCase:
    repository_mock: Mock
    use_case: ToggleHorseActivationUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(HorsesRepository, instance=True)
        self.use_case = ToggleHorseActivationUseCase(repository=self.repository_mock)

    def test_should_toggle_horse_activation_and_replace_it_when_horse_exists(
        self,
    ) -> None:
        existing_horse = HorsesFaker.fake(is_active=True)
        owner_id = IdFaker.fake().value
        self.repository_mock.find_by_id_and_owner_id.return_value = existing_horse

        result = self.use_case.execute(
            horse_id=existing_horse.id.value,
            owner_id=owner_id,
        )

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.repository_mock.replace.assert_called_once()

        searched_horse_id = self.repository_mock.find_by_id_and_owner_id.call_args[0][0]
        searched_owner_id = self.repository_mock.find_by_id_and_owner_id.call_args[0][1]
        replaced_horse = self.repository_mock.replace.call_args[0][0]

        assert searched_horse_id == existing_horse.id
        assert searched_owner_id.value == owner_id
        assert replaced_horse.id == existing_horse.id
        assert replaced_horse.is_active.value is False
        assert result == replaced_horse.dto

    def test_should_raise_horse_not_found_error_when_horse_does_not_exist(self) -> None:
        horse_id = IdFaker.fake().value
        owner_id = IdFaker.fake().value
        self.repository_mock.find_by_id_and_owner_id.return_value = None

        with pytest.raises(HorseNotFoundError):
            self.use_case.execute(horse_id=horse_id, owner_id=owner_id)

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.repository_mock.replace.assert_not_called()
