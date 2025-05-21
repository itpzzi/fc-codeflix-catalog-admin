from pathlib import Path

import pytest

from src.core._shared.infra.storage.local_storage import LocalStorage
from src.core.video.application.usecases.upload_video import UploadVideo
from src.core.video.domain.value_objects import (
    AudioVideoMedia,
    Duration,
    LaunchYear,
    MediaStatus,
    MediaType,
    Rating,
)
from src.core.video.domain.video import Video
from src.core.video.infra.in_memory_video_repository import InMemoryVideoRepository


@pytest.fixture
def local_storage(tmp_path) -> LocalStorage:
    return LocalStorage(bucket=tmp_path)


@pytest.fixture
def repository():
    return InMemoryVideoRepository()


@pytest.fixture
def valid_data():
    return dict(
        title="Integration Title",
        description="Integration Description",
        duration=Duration(120),
        launch_year=LaunchYear(2022),
        rating=Rating.AGE_12,
        opened=False,
        categories=set(),
        genres=set(),
        cast_members=set(),
    )


def test_upload_video_integration(valid_data, local_storage, repository, tmp_path):
    video = Video(**valid_data)
    repository.save(video)

    file_name = "integration_test.mp4"
    content = b"video binary content"
    content_type = "video/mp4"

    use_case = UploadVideo(repository=repository, storage=local_storage)
    input = UploadVideo.Input(
        video_id=video.id,
        file_name=file_name,
        content_type=content_type,
        content=content,
    )

    use_case.execute(input)

    updated_video = repository.get_by_id(video.id)
    assert updated_video.video is not None

    raw_location = Path("videos") / f"{updated_video.id}" / f"{file_name}"
    assert updated_video.video == AudioVideoMedia(
        name=file_name,
        raw_location=str(raw_location),
        encoded_location="",
        status=MediaStatus.PENDING,
        media_type=MediaType.VIDEO,
    )

    expected_path = tmp_path / raw_location

    assert expected_path.exists()
    with open(expected_path, "rb") as f:
        assert f.read() == content
