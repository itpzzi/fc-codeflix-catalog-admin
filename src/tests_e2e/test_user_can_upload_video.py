import os
from pathlib import Path
from uuid import UUID

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import status
from rest_framework.test import APIClient

from src.core.video.domain.value_objects import Duration, LaunchYear, Rating
from src.core.video.domain.video import Video
from src.django_project.video_app.models import (
    AudioVideoMedia as AudioVideoMediaModel,
)
from src.django_project.video_app.views import local_storage, video_repository


@pytest.fixture
def valid_data():
    return dict(
        id=UUID("64d4a068-8f79-48a5-8b90-8c8543ea48b2"),
        title="Test Title",
        description="Test Description",
        duration=Duration(150),
        launch_year=LaunchYear(2023),
        rating=Rating(Rating.AGE_10),
        opened=True,
        categories=set(),
        genres=set(),
        cast_members=set(),
    )


@pytest.fixture
def valid_video(valid_data):
    return Video(**valid_data)


@pytest.mark.django_db
class TestUploadVideoE2E:

    def test_upload_video_success_saves_file_locally(self, valid_video):

        video_repository.save(valid_video)

        dummy_content = b"dummy mp4 content"
        file_name = "test_video.mp4"
        content_type = "video/mp4"

        mock_video_file = SimpleUploadedFile(
            name=file_name, content=dummy_content, content_type=content_type
        )

        safe_path = Path("videos") / f"{valid_video.id}" / f"{file_name}"

        url = f"/api/videos/{valid_video.id}/"
        data = {"video_file": mock_video_file}

        client = APIClient()
        response = client.patch(url, data=data, format="multipart")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert AudioVideoMediaModel.objects.count() == 1

        saved_path = local_storage.bucket / safe_path
        assert saved_path.exists()
        with open(saved_path, "rb") as f:
            content = f.read()
        assert content == dummy_content

        os.remove(saved_path)

    def test_upload_video_invalid_fails_and_no_file_saved(self, valid_video):
        video_repository.save(valid_video)

        dummy_content = b""
        file_name = "test_audio.mp3"
        content_type = "audio/mp3"

        mock_video_file = SimpleUploadedFile(
            name=file_name, content=dummy_content, content_type=content_type
        )

        safe_path = Path("videos") / f"{valid_video.id}" / f"{file_name}"

        url = f"/api/videos/{valid_video.id}/"
        data = {"video_file": mock_video_file}

        client = APIClient()
        response = client.patch(url, data=data, format="multipart")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "video_file" in response.data
        assert "The submitted file is empty." in response.data.get("video_file", "")

        saved_path = local_storage.bucket / safe_path
        assert not saved_path.exists()
