import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from src.django_project.video_app.models import Video as VideoModel


@pytest.mark.django_db
class TestCreateVideoAPI:

    def test_create_video_api_with_valid_data(self):
        url = "/api/videos/"
        data = {
            "title": "Test Video",
            "description": "This is a test video.",
            "duration": 60,
            "launch_year": 2023,
            "opened": False,
            "rating": "AGE_10",
            "categories": set(),
            "genres": set(),
            "cast_members": set(),
        }

        response = APIClient().post(url, data=data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        assert VideoModel.objects.count() == 1
        assert response.data.get("id") is not None
        assert str(response.data.get("id")) == str(VideoModel.objects.first().id)

    def test_rejects_create_video_api_with_invalid_data(self):
        url = "/api/videos/"
        data = {
            "title": "a" * 256,
            "description": None,
            "duration": -1,
            "launch_year": 1700,
            "opened": False,
            "rating": "AGE_99",
            "categories": ["id-fake"],
            "genres": ["id-fake"],
            "cast_members": None,
        }

        response = APIClient().post(url, data=data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert VideoModel.objects.count() == 0
        assert response.data == {
            "title": ["Ensure this field has no more than 255 characters."],
            "description": ["This field may not be null."],
            "launch_year": ["Ensure this value is greater than or equal to 1900."],
            "duration": ["Ensure this value is greater than or equal to 0.0."],
            "rating": ['"AGE_99" is not a valid choice.'],
            "categories": {0: ["Must be a valid UUID."]},
            "genres": {0: ["Must be a valid UUID."]},
            "cast_members": ["This field may not be null."],
        }

    def test_rejects_create_video_with_invalid_related_entities(self):
        url = "/api/videos/"
        data = {
            "title": "A Fake Video",
            "description": "A fake video description",
            "launch_year": 2025,
            "duration": 150,
            "rating": "L",
            "categories": [str(uuid.uuid4())],
            "genres": [str(uuid.uuid4())],
            "cast_members": [str(uuid.uuid4())],
        }

        response = APIClient().post(url, data=data, format="json")

        error_messages = "; ".join(
            [
                "Invalid categories",
                "Invalid genres",
                "Invalid cast members",
            ]
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert VideoModel.objects.count() == 0
        assert response.data.get("error") == error_messages
