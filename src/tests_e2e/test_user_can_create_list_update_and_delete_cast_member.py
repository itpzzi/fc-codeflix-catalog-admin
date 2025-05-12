import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.mark.django_db
class TestCreateAndDeleteCastMember:

    def test_user_can_create_and_delete_cast_member(
        self, api_client: APIClient
    ) -> None:
        # Verifica que a lista de membros está inicialmente vazia
        response = api_client.get("/api/cast-members/")
        assert response.status_code == 200
        assert response.data == {"data": []}

        # Criação de uma novo membro
        create_url = "/api/cast-members/"
        create_payload = {"name": "Zombie", "type": "director"}
        create_response = api_client.post(create_url, data=create_payload)
        assert create_response.status_code == 201
        created_cast_member_id = create_response.data["id"]

        # Verifica que o membro criado aparece na listagem
        list_response = api_client.get("/api/cast-members/")
        assert list_response.status_code == 200
        assert list_response.data == {
            "data": [
                {"id": created_cast_member_id, "name": "Zombie", "type": "director"}
            ]
        }

        # Verifica que o membro criado rejeita ser atualizado com parâmetros inválidos
        update_url = f"/api/cast-members/{created_cast_member_id}/"
        update_payload = {"name": "Steve... Again", "type": "producer"}
        update_response = api_client.put(update_url, data=update_payload)
        assert update_response.status_code == 400
        assert '"producer" is not a valid choice.' in update_response.data["type"]

        # Exclusão do membro
        delete_url = f"/api/cast-members/{created_cast_member_id}/"
        delete_response = api_client.delete(delete_url)
        assert delete_response.status_code == 204

        # Verifica que a lista de membros está novamente vazia
        final_list_response = api_client.get("/api/cast-members/")
        assert final_list_response.status_code == 200
        assert final_list_response.data == {"data": []}
