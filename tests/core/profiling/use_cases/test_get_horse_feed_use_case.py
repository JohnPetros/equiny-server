import pytest
from unittest.mock import Mock, create_autospec

from src.equiny.core.profiling.domain.structures.dtos.age_range_dto import AgeRangeDto
from src.equiny.core.profiling.interfaces.repositories import HorsesRepository
from src.equiny.core.profiling.use_cases.get_horse_feed_use_case import GetHorseFeedUseCase
from src.equiny.core.shared.responses.pagination_response import PaginationResponse
from tests.fakers.profiling.structures.feed_horse_faker import FeedHorseFaker
from tests.fakers.shared.structures.id_faker import IdFaker


class TestGetHorseFeedUseCase:
    repository_mock: Mock
    use_case: GetHorseFeedUseCase

    @pytest.fixture(autouse=True)
    def setup_tests(self) -> None:
        self.repository_mock = create_autospec(HorsesRepository, instance=True)
        self.use_case = GetHorseFeedUseCase(repository=self.repository_mock)

    def test_should_call_repository_with_correct_parameters(self) -> None:
        horse_id = IdFaker.fake().value
        sex = 'female'
        breeds = ['quarto de milha', 'mangalarga marchador']
        age_range_dto = AgeRangeDto(min_age=3, max_age=10)
        max_distance_in_km = 120
        cursor = None
        limit = 20

        feed_horse = FeedHorseFaker.fake()
        pagination_response = PaginationResponse(
            items=[feed_horse],
            next_cursor=None,
            has_more=False,
        )
        self.repository_mock.find_many_feed_horses.return_value = pagination_response

        self.use_case.execute(
            horse_id=horse_id,
            sex=sex,
            breeds=breeds,
            age_range_dto=age_range_dto,
            max_distance_in_km=max_distance_in_km,
            cursor=cursor,
            limit=limit,
        )

        self.repository_mock.find_many_feed_horses.assert_called_once()
        call_kwargs = self.repository_mock.find_many_feed_horses.call_args[1]
        assert call_kwargs['limit'] == limit

    def test_should_return_pagination_response_with_feed_horse_dto(self) -> None:
        horse_id = IdFaker.fake().value
        sex = 'female'
        breeds: list[str] = []
        age_range_dto = AgeRangeDto(min_age=0, max_age=30)
        max_distance_in_km = 75
        cursor = None
        limit = 10

        feed_horse = FeedHorseFaker.fake()
        pagination_response = PaginationResponse(
            items=[feed_horse],
            next_cursor=None,
            has_more=False,
        )
        self.repository_mock.find_many_feed_horses.return_value = pagination_response

        result = self.use_case.execute(
            horse_id=horse_id,
            sex=sex,
            breeds=breeds,
            age_range_dto=age_range_dto,
            max_distance_in_km=max_distance_in_km,
            cursor=cursor,
            limit=limit,
        )

        assert result.items[0] == feed_horse.dto
        assert result.has_more is False

    def test_should_handle_cursor_properly(self) -> None:
        horse_id = IdFaker.fake().value
        sex = 'male'
        breeds: list[str] = []
        age_range_dto = AgeRangeDto(min_age=0, max_age=30)
        max_distance_in_km = 40
        cursor = IdFaker.fake().value
        limit = 5

        feed_horse = FeedHorseFaker.fake()
        pagination_response = PaginationResponse(
            items=[feed_horse],
            next_cursor=feed_horse.horse.id.value,
            has_more=True,
        )
        self.repository_mock.find_many_feed_horses.return_value = pagination_response

        result = self.use_case.execute(
            horse_id=horse_id,
            sex=sex,
            breeds=breeds,
            age_range_dto=age_range_dto,
            max_distance_in_km=max_distance_in_km,
            cursor=cursor,
            limit=limit,
        )

        self.repository_mock.find_many_feed_horses.assert_called_once()
        call_kwargs = self.repository_mock.find_many_feed_horses.call_args[1]
        assert call_kwargs['cursor'] is not None
        assert result.has_more is True
        assert result.next_cursor == feed_horse.horse.id.value
