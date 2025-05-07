import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestCreateAndDeleteCategory:

    def test_user_can_create_and_delete_category(self, api_client: APIClient) -> None:
        # Verifica que a lista de categorias está inicialmente vazia
        response = api_client.get("/api/categories/")
        assert response.status_code == 200
        assert response.data == {"data": []}

        # Criação de uma nova categoria
        create_url = "/api/categories/"
        create_payload = {
            "name": "Documentário",
            "description": "Informações relevantes",
            "is_active": True,
        }
        create_response = api_client.post(create_url, data=create_payload)
        assert create_response.status_code == 201
        created_category_id = create_response.data["id"]

        # Verifica que a categoria criada aparece na listagem
        list_response = api_client.get("/api/categories/")
        assert list_response.status_code == 200
        assert list_response.data == {
            "data": [
                {
                    "id": created_category_id,
                    "name": "Documentário",
                    "description": "Informações relevantes",
                    "is_active": True,
                }
            ]
        }

        # Exclusão da categoria
        delete_url = f"/api/categories/{created_category_id}/"
        delete_response = api_client.delete(delete_url)
        assert delete_response.status_code == 204

        # Verifica que a lista de categorias está novamente vazia
        final_list_response = api_client.get("/api/categories/")
        assert final_list_response.status_code == 200
        assert final_list_response.data == {"data": []}
