import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from src.core._shared.config import DEFAULT_PAGE_SIZE


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def created_categories(api_client: APIClient) -> dict:
    url = "/api/categories/"
    categories = {
        "Filme": api_client.post(url, {"name": "Filme"}).data["id"],
        "Série": api_client.post(url, {"name": "Série"}).data["id"],
        "Documentário": api_client.post(url, {"name": "Documentário"}).data["id"],
    }
    return categories


@pytest.mark.django_db
class TestGenreAPI:
    def test_user_can_crud_genres_with_pagination_and_ordering(
        self, api_client: APIClient, created_categories: dict
    ) -> None:
        list_url = "/api/genres/"

        # Verifica lista inicial vazia
        response = api_client.get(list_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            "data": [],
            "meta": {
                "current_page": 1,
                "per_page": DEFAULT_PAGE_SIZE,
                "total": 0,
            },
        }

        # Define categorias para cada gênero
        ids = created_categories
        payloads = [
            {
                "name": "Drama",
                "is_active": True,
                "categories": [ids["Filme"], ids["Série"], ids["Documentário"]],
            },
            {
                "name": "Terror",
                "is_active": True,
                "categories": [ids["Filme"], ids["Série"]],
            },
            {
                "name": "Ação",
                "is_active": True,
                "categories": [ids["Filme"], ids["Série"]],
            },
            {"name": "Romance", "is_active": False, "categories": []},
        ]

        genre_ids = {}
        for payload in payloads:
            resp = api_client.post(list_url, data=payload)
            assert resp.status_code == status.HTTP_201_CREATED
            genre_ids[payload["name"]] = resp.data["id"]

        # Verifica ordenação e paginação (página 2, ordenado por nome ascendente)
        params = "?order_by=name&reverse=False&current_page=2&per_page=2"
        response = api_client.get(f"{list_url}{params}")
        assert response.status_code == status.HTTP_200_OK

        expected_data = [
            {
                "id": genre_ids["Romance"],
                "name": "Romance",
                "is_active": False,
                "categories": [],
            },
            {
                "id": genre_ids["Terror"],
                "name": "Terror",
                "is_active": True,
                "categories": [ids["Filme"], ids["Série"]],
            },
        ]

        received = sorted(response.data["data"], key=lambda x: x["name"])
        expected = sorted(expected_data, key=lambda x: x["name"])

        for rec, exp in zip(received, expected):
            assert rec["id"] == exp["id"]
            assert rec["name"] == exp["name"]
            assert rec["is_active"] == exp["is_active"]
            assert set(rec["categories"]) == set(exp["categories"])

        assert response.data["meta"] == {
            "total": 4,
            "current_page": 2,
            "per_page": DEFAULT_PAGE_SIZE,
        }

        # Testa falha ao atualizar com categorias inválidas
        invalid_ids = [str(uuid.uuid4()), str(uuid.uuid4())]
        update_url = f"/api/genres/{genre_ids['Romance']}/"
        update_payload = {
            "name": "Romance",
            "is_active": False,
            "categories": invalid_ids,
        }
        update_response = api_client.put(update_url, data=update_payload)
        assert update_response.status_code == status.HTTP_400_BAD_REQUEST

        # Deleta gênero e verifica remoção
        delete_url = f"/api/genres/{genre_ids['Romance']}/"
        delete_response = api_client.delete(delete_url)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verifica lista final com meta
        final_response = api_client.get(list_url)
        assert final_response.status_code == status.HTTP_200_OK
        assert final_response.data["meta"]["total"] == 3
