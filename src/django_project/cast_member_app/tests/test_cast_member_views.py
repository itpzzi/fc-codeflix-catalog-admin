from urllib.request import Request
from uuid import UUID
import uuid
from rest_framework.test import APIClient
from rest_framework import status
import pytest

from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.django_project.cast_member_app.repository import DjangoORMCastMemberRepository


@pytest.fixture
def repository():
    return DjangoORMCastMemberRepository()


@pytest.fixture
def actor_member():
    return CastMember(name="Steve", type=CastMemberType.ACTOR)


@pytest.fixture
def director_member():
    return CastMember(name="Zombie", type=CastMemberType.DIRECTOR)


@pytest.mark.django_db
class TestCreateAPI:
    def test_create_cast_member(self, actor_member, repository):
        url = "/api/cast_members/"
        data = {
            "name": actor_member.name,
            "type": actor_member.type,
        }

        response = APIClient().post(url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data

        id_str = response.data.get("id")
        assert isinstance(id_str, str)

        try:
            created_id = uuid.UUID(id_str, version=4)
        except ValueError:
            assert False, "ID retornado não é um UUID v4 válido"

        created_item = repository.get_by_id(id=created_id)
        assert created_item is not None
        assert created_item.name == actor_member.name
        assert created_item.type == actor_member.type

    def test_raises_400_for_invalid_payload(self, actor_member):
        url = "/api/cast_members/"
        data = {"name": actor_member.name, "type": "producer"}

        response = APIClient().post(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "type" in response.data
        assert '"producer" is not a valid choice.' in response.data.get("type")


@pytest.mark.django_db
class TestListAPI:
    def test_list_all_repository(self, actor_member, director_member, repository):
        repository.save(director_member)
        repository.save(actor_member)

        expected_data = {
            "data": [
                {
                    "name": actor_member.name,
                    "type": actor_member.type,
                    "id": str(actor_member.id),
                },
                {
                    "name": director_member.name,
                    "type": director_member.type,
                    "id": str(director_member.id),
                },
            ]
        }

        url = "/api/cast_members/"
        response = APIClient().get(url)

        assert response.data == expected_data
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeleteAPI:
    def test_raise_400_for_invalid_pk(self):
        url = "/api/cast_members/invalid_id/"

        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"id": ["Must be a valid UUID."]}

    def test_raise_404_for_nonexistent_cast_member(self):
        fake_id = uuid.uuid4()
        url = f"/api/cast_members/{fake_id}/"

        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_an_existent_cast_member(self, actor_member, repository):
        repository.save(actor_member)
        url = f"/api/cast_members/{actor_member.id}/"

        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.django_db
class TestUpdateAPI:
    def test_when_request_data_is_invalid_then_return_400(self):
        url = "/api/cast_members/invalid_id/"
        data = {"name": "", "type": "producer"}

        response = APIClient().put(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "id" in response.data
        assert "name" in response.data
        assert "type" in response.data

        assert "Must be a valid UUID." in response.data.get("id")
        assert "This field may not be blank." in response.data.get("name")
        assert '"producer" is not a valid choice.' in response.data.get("type")

    def test_when_member_does_not_exist_then_return_404(self, actor_member, repository):
        repository.save(actor_member)

        url = f"/api/cast_members/{uuid.uuid4()}/"
        data = {"name": actor_member.name, "type": actor_member.type}

        response = APIClient().put(url, data=data, format="json")

        assert response is not None
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_when_request_data_is_valid_then_update_member(
        self, actor_member, repository
    ):
        repository.save(actor_member)

        url = f"/api/cast_members/{actor_member.id}/"
        data = {"name": "Skeleton", "type": CastMemberType.DIRECTOR}

        response = APIClient().put(url, data=data, format="json")

        assert response is not None
        assert response.status_code == status.HTTP_204_NO_CONTENT

        updated_item = repository.get_by_id(actor_member.id)
        assert updated_item is not None
        assert updated_item.name == "Skeleton"
        assert updated_item.type == CastMemberType.DIRECTOR
