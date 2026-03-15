import pytest
from unittest.mock import Mock, create_autospec

from src.equiny.core.matching.use_cases.view_match_use_case import ViewHorseMatchUseCase
from src.equiny.core.profiling.domain.errors.horse_not_found_error import (
    HorseNotFoundError,
)
from src.equiny.core.profiling.domain.errors.horse_match_not_found_error import (
    HorseMatchNotFoundError,
)
from src.equiny.core.profiling.interfaces.repositories import HorsesRepository
from tests.fakers.profiling.entities.horses_faker import HorsesFaker
from tests.fakers.profiling.structures.horse_match_faker import HorseMatchFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestViewHorseMatchUseCase:
    repository_mock: Mock
    use_case: ViewHorseMatchUseCase

    @pytest.fixture(autouse=True)
    def setup(self) -> None:
        self.repository_mock = create_autospec(HorsesRepository, instance=True)
        self.use_case = ViewHorseMatchUseCase(repository=self.repository_mock)

    def test_should_return_viewed_match_and_update_repository(self) -> None:
        owner_id = IdFaker.fake().value
        from_horse_id = IdFaker.fake().value
        to_horse_id = IdFaker.fake().value
        horse = HorsesFaker.fake(id=from_horse_id)
        horse_match = HorseMatchFaker.fake(
            owner_horse_id=to_horse_id,
            is_viewed=False,
        )
        self.repository_mock.find_by_id_and_owner_id.return_value = horse
        self.repository_mock.find_horse_match_by_horses.return_value = horse_match

        result = self.use_case.execute(
            owner_id=owner_id,
            from_horse_id=from_horse_id,
            to_horse_id=to_horse_id,
        )

        assert result.is_viewed is True
        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        call_args = self.repository_mock.find_by_id_and_owner_id.call_args[0]
        assert call_args[0].value == from_horse_id
        assert call_args[1].value == owner_id
        self.repository_mock.find_horse_match_by_horses.assert_called_once_with(
            horse.id, horse_match.owner_horse_id
        )
        self.repository_mock.replace_horse_match.assert_called_once()
        captured_args = self.repository_mock.replace_horse_match.call_args[0]
        assert captured_args[0] == horse.id
        assert captured_args[1].value == to_horse_id
        assert captured_args[2].is_viewed.is_true

    def test_should_raise_horse_not_found_error_when_horse_does_not_exist(self) -> None:
        owner_id = IdFaker.fake().value
        from_horse_id = IdFaker.fake().value
        to_horse_id = IdFaker.fake().value
        self.repository_mock.find_by_id_and_owner_id.return_value = None

        with pytest.raises(HorseNotFoundError):
            self.use_case.execute(
                owner_id=owner_id,
                from_horse_id=from_horse_id,
                to_horse_id=to_horse_id,
            )

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        self.repository_mock.find_horse_match_by_horses.assert_not_called()
        self.repository_mock.replace_horse_match.assert_not_called()

    def test_should_raise_horse_match_not_found_error_when_match_does_not_exist(
        self,
    ) -> None:
        owner_id = IdFaker.fake().value
        from_horse_id = IdFaker.fake().value
        to_horse_id = IdFaker.fake().value
        horse = HorsesFaker.fake(id=from_horse_id)
        self.repository_mock.find_by_id_and_owner_id.return_value = horse
        self.repository_mock.find_horse_match_by_horses.return_value = None

        with pytest.raises(HorseMatchNotFoundError):
            self.use_case.execute(
                owner_id=owner_id,
                from_horse_id=from_horse_id,
                to_horse_id=to_horse_id,
            )

        self.repository_mock.find_by_id_and_owner_id.assert_called_once()
        call_args = self.repository_mock.find_by_id_and_owner_id.call_args[0]
        assert call_args[0].value == from_horse_id
        assert call_args[1].value == owner_id
        self.repository_mock.find_horse_match_by_horses.assert_called_once()
        match_call_args = self.repository_mock.find_horse_match_by_horses.call_args[0]
        assert match_call_args[0] == horse.id
        assert match_call_args[1].value == to_horse_id
        self.repository_mock.replace_horse_match.assert_not_called()
