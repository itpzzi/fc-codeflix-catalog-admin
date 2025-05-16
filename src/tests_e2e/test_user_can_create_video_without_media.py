import pytest
from rest_framework import status
from rest_framework.test import APIClient

from src.django_project.video_app.models import Video as VideoModel


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def created_dependencies(api_client: APIClient) -> dict:
    categories_response = api_client.post("/api/categories/", {"name": "Filme"})
    id_category = categories_response.data["id"]

    genre_response = api_client.post(
        "/api/genres/", {"name": "Ação", "is_active": True, "categories": [id_category]}
    )
    genre_id = genre_response.data["id"]

    cast_members_response = api_client.post(
        "/api/cast_members/", {"name": "Steve", "type": "actor"}
    )
    cast_member_id = cast_members_response.data["id"]

    return {
        "category_id": id_category,
        "genre_id": genre_id,
        "cast_member_id": cast_member_id,
    }


@pytest.mark.django_db
class TestVideoE2E:

    def test_create_video_success(
        self, api_client: APIClient, created_dependencies: dict
    ):
        url = "/api/videos/"
        data = {
            "title": "Filme E2E",
            "description": "Descrição qualquer",
            "duration": 90.0,
            "launch_year": 2024,
            "opened": True,
            "rating": "AGE_14",
            "categories": [created_dependencies["category_id"]],
            "genres": [created_dependencies["genre_id"]],
            "cast_members": [created_dependencies["cast_member_id"]],
        }

        response = api_client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert VideoModel.objects.count() == 1
        model = VideoModel.objects.first()
        assert str(response.data["id"]) == str(model.id)

    def test_create_video_fail_with_invalid_payload(self, api_client: APIClient):
        url = "/api/videos/"
        data = {
            "title": "a" * 256,
            "description": None,
            "duration": -10,
            "launch_year": 1800,
            "opened": False,
            "rating": "FAKE",
            "categories": ["invalid-id"],
            "genres": ["invalid-id"],
            "cast_members": None,
        }

        response = api_client.post(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert VideoModel.objects.count() == 0
        assert response.data == {
            "title": ["Ensure this field has no more than 255 characters."],
            "description": ["This field may not be null."],
            "launch_year": ["Ensure this value is greater than or equal to 1900."],
            "duration": ["Ensure this value is greater than or equal to 0.0."],
            "rating": ['"FAKE" is not a valid choice.'],
            "categories": {0: ["Must be a valid UUID."]},
            "genres": {0: ["Must be a valid UUID."]},
            "cast_members": ["This field may not be null."],
        }
