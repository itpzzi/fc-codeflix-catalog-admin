from pathlib import Path
from unittest.mock import create_autospec
from uuid import uuid4

import pytest

from src.core._shared.infra.storage.abstract_storage_service import (
    AbstractStorageService,
)
from src.core.video.application.exceptions import VideoNotFound
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
from src.core.video.domain.video_repository import IVideoRepository


@pytest.fixture
def valid_data():
    return dict(
        title="Test Title",
        description="Test Description",
        duration=Duration(150),
        launch_year=LaunchYear(2023),
        rating=Rating(Rating.AGE_16),
        opened=True,
        categories=set(),
        genres=set(),
        cast_members=set(),
    )


@pytest.fixture
def valid_video(valid_data):
    return Video(**valid_data)


@pytest.fixture
def mock_repository() -> IVideoRepository:
    repository = create_autospec(IVideoRepository)
    return repository


@pytest.fixture
def mock_storage() -> AbstractStorageService:
    storage_service = create_autospec(AbstractStorageService)
    return storage_service


class TestUploadVideo:
    def test_should_upload_video(
        self,
        valid_video: Video,
        mock_storage: AbstractStorageService,
        mock_repository: IVideoRepository,
    ):

        mock_repository.get_by_id.return_value = valid_video

        file_name = "test.mp4"
        content_type = "video/mp4"
        content = b"some video data"
        full_path = Path("videos") / f"{valid_video.id}" / f"{file_name}"

        input = UploadVideo.Input(
            video_id=valid_video.id,
            file_name=file_name,
            content_type=content_type,
            content=content,
        )

        use_case = UploadVideo(repository=mock_repository, storage=mock_storage)

        use_case.execute(input)

        mock_storage.store.assert_called_once_with(
            file_name=full_path, content_type=content_type, content=content
        )
        assert mock_repository.update.called is True
        assert valid_video.video is not None

        assert valid_video.video == AudioVideoMedia(
            name=file_name,
            raw_location=str(full_path),
            encoded_location="",
            status=MediaStatus.PENDING,
            media_type=MediaType.VIDEO,
        )

    def test_should_raise_video_not_found_when_video_does_not_exist(
        self, mock_repository: IVideoRepository, mock_storage: AbstractStorageService
    ):
        mock_repository.get_by_id.return_value = None

        video_id = uuid4()
        input_data = UploadVideo.Input(
            video_id=video_id,
            file_name="nonexistent.mp4",
            content_type="video/mp4",
            content=b"fake data",
        )

        use_case = UploadVideo(repository=mock_repository, storage=mock_storage)

        with pytest.raises(
            VideoNotFound,
            match=f"Cannot update non-existent video. {video_id} not found",
        ):
            use_case.execute(input_data)
