import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestRetrieveAndUpdateCategory:

    def test_user_can_retrieve_and_update_category(self, api_client: APIClient) -> None:
        # Criação da categoria
        create_url = "/api/categories/"
        create_payload = {
            "name": "Aventura",
            "description": "Filmes com ação e exploração",
            "is_active": True,
        }
        create_response = api_client.post(create_url, data=create_payload)
        assert create_response.status_code == 201
        category_id = create_response.data["id"]

        # Recuperação (GET) da categoria criada
        retrieve_url = f"/api/categories/{category_id}/"
        retrieve_response = api_client.get(retrieve_url)
        assert retrieve_response.status_code == 200
        assert retrieve_response.data == {
            "data": {
                "id": category_id,
                "name": "Aventura",
                "description": "Filmes com ação e exploração",
                "is_active": True,
            }
        }

        # Atualização (PUT) da categoria
        update_payload = {
            "id": category_id,
            "name": "Aventura Atualizada",
            "description": "Exploração intensa",
            "is_active": False,
        }
        update_response = api_client.put(retrieve_url, data=update_payload)
        assert update_response.status_code == 204

        # Recuperação novamente para verificar atualização
        updated_retrieve_response = api_client.get(retrieve_url)
        assert updated_retrieve_response.status_code == 200
        assert updated_retrieve_response.data == {
            "data": {
                "id": category_id,
                "name": "Aventura Atualizada",
                "description": "Exploração intensa",
                "is_active": False,
            }
        }
