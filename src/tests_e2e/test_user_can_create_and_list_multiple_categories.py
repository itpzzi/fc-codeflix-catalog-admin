import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestCreateAndListMultipleCategories:

    def test_user_can_create_and_list_multiple_categories(
        self, api_client: APIClient
    ) -> None:
        # Verifica que a lista de categorias está inicialmente vazia
        initial_response = api_client.get("/api/categories/")
        assert initial_response.status_code == 200
        assert initial_response.data == {"data": []}

        # Criação de múltiplas categorias
        create_url = "/api/categories/"
        categories_to_create = [
            {"name": "Drama", "description": "Filmes emocionantes", "is_active": False},
            {"name": "Comédia", "description": "Filmes engraçados", "is_active": True},
        ]

        created_categories = []
        for payload in categories_to_create:
            response = api_client.post(create_url, data=payload)
            assert response.status_code == 201
            created_categories.append({"id": response.data["id"], **payload})

        # Listagem final das categorias
        list_response = api_client.get("/api/categories/")
        assert list_response.status_code == 200

        # Ordena as duas listas por nome para comparação estável
        expected_sorted = sorted(created_categories, key=lambda x: x["name"])
        actual_sorted = sorted(list_response.data["data"], key=lambda x: x["name"])

        assert actual_sorted == expected_sorted
