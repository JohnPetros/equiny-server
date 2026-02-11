from datetime import datetime

import pytest
from fastapi.testclient import TestClient


class TestCreateHorseController:
    def test_should_create_horse_and_return_payload(self, client: TestClient) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'Test Horse',
                'birth_month': 1,
                'birth_year': 2020,
                'breed': 'arabe',
            },
        )

        assert response.status_code == 201

        data = response.json()
        assert data['id']
        assert data['name'] == 'Test Horse'
        assert data['birth_month'] == 1
        assert data['birth_year'] == 2020
        assert data['breed'] == 'arabe'

    @pytest.mark.parametrize('birth_month', [0, 13])
    def test_should_return_422_when_birth_month_is_invalid(
        self, client: TestClient, birth_month: int
    ) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'Test Horse',
                'birth_month': birth_month,
                'birth_year': 2020,
                'breed': 'arabe',
            },
        )

        assert response.status_code == 422

    def test_should_return_422_when_birth_year_is_in_the_future(
        self, client: TestClient
    ) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'Test Horse',
                'birth_month': 1,
                'birth_year': datetime.now().year + 1,
                'breed': 'arabe',
            },
        )

        assert response.status_code == 422

    def test_should_return_422_when_breed_is_invalid(self, client: TestClient) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'Test Horse',
                'birth_month': 1,
                'birth_year': 2020,
                'breed': 'invalid breed',
            },
        )

        assert response.status_code == 422

    def test_should_return_422_when_name_is_too_short(self, client: TestClient) -> None:
        response = client.post(
            '/profiling/horses',
            json={
                'name': 'AB',
                'birth_month': 1,
                'birth_year': 2020,
                'breed': 'arabe',
            },
        )

        assert response.status_code == 422
