import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.django_project.cast_member_app.repository import DjangoORMCastMemberRepository


@pytest.fixture
def cast_members():
    return {
        "actor": CastMember(name="Steve", type=CastMemberType.ACTOR),
        "director": CastMember(name="Zombie", type=CastMemberType.DIRECTOR),
        "actor2": CastMember(name="Spider", type=CastMemberType.ACTOR),
        "director2": CastMember(name="Skeleton", type=CastMemberType.DIRECTOR),
    }


@pytest.fixture
def repository():
    return DjangoORMCastMemberRepository()


@pytest.mark.django_db
class TestCastMemberAPI:
    def setup_test_data(self, repository, cast_members, selected_members=None):
        """Helper to setup test data"""
        for member_name, member in cast_members.items():
            if selected_members is None or member_name in selected_members:
                repository.save(member)

    def test_create_cast_member(self, cast_members, repository):
        url = "/api/cast_members/"
        data = {
            "name": cast_members["actor"].name,
            "type": cast_members["actor"].type,
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
        assert created_item.name == cast_members["actor"].name
        assert created_item.type == cast_members["actor"].type

    def test_create_with_invalid_payload(self, cast_members):
        url = "/api/cast_members/"
        data = {"name": cast_members["actor"].name, "type": "producer"}

        response = APIClient().post(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "type" in response.data
        assert '"producer" is not a valid choice.' in response.data.get("type")

    def test_list_cast_members(self, cast_members, repository):
        self.setup_test_data(
            repository,
            {"actor": cast_members["actor"], "director": cast_members["director"]},
        )

        expected_data = {
            "data": [
                {
                    "name": cast_members["actor"].name,
                    "type": cast_members["actor"].type,
                    "id": str(cast_members["actor"].id),
                },
                {
                    "name": cast_members["director"].name,
                    "type": cast_members["director"].type,
                    "id": str(cast_members["director"].id),
                },
            ]
        }

        url = "/api/cast_members/"
        response = APIClient().get(url)

        assert response.data == expected_data
        assert response.status_code == status.HTTP_200_OK

    @pytest.mark.parametrize(
        "order_by,reverse,current_page,per_page,expected_names",
        [
            ("name", False, 1, 2, ["Skeleton", "Spider"]),
            ("name", False, 2, 2, ["Steve", "Zombie"]),
            ("name", True, 1, 2, ["Zombie", "Steve"]),
            ("name", True, 2, 2, ["Spider", "Skeleton"]),
        ],
    )
    def test_list_cast_members_ordered_and_paginated(
        self,
        order_by,
        reverse,
        current_page,
        per_page,
        expected_names,
        cast_members,
        repository,
    ):
        self.setup_test_data(repository, cast_members)

        url = f"/api/cast_members/?order_by={order_by}&reverse={reverse}&current_page={current_page}&per_page={per_page}"
        response = APIClient().get(url)

        returned_names = [member["name"] for member in response.data["data"]]

        assert response.status_code == status.HTTP_200_OK
        assert returned_names == expected_names

    def test_delete_with_invalid_id(self):
        url = "/api/cast_members/invalid_id/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"id": ["Must be a valid UUID."]}

    def test_delete_nonexistent_cast_member(self):
        url = f"/api/cast_members/{uuid.uuid4()}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_existing_cast_member(self, cast_members, repository):
        self.setup_test_data(repository, {"actor": cast_members["actor"]})

        url = f"/api/cast_members/{cast_members['actor'].id}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_update_with_invalid_data(self):
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

    def test_update_nonexistent_cast_member(self, cast_members, repository):
        self.setup_test_data(repository, {"actor": cast_members["actor"]})

        url = f"/api/cast_members/{uuid.uuid4()}/"
        data = {"name": cast_members["actor"].name, "type": cast_members["actor"].type}

        response = APIClient().put(url, data=data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_with_valid_data(self, cast_members, repository):
        self.setup_test_data(repository, {"actor": cast_members["actor"]})

        url = f"/api/cast_members/{cast_members['actor'].id}/"
        data = {"name": "Skeleton", "type": CastMemberType.DIRECTOR}

        response = APIClient().put(url, data=data, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT

        updated_item = repository.get_by_id(cast_members["actor"].id)
        assert updated_item is not None
        assert updated_item.name == "Skeleton"
        assert updated_item.type == CastMemberType.DIRECTOR
