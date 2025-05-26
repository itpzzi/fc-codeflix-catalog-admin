from unittest.mock import Mock
from uuid import uuid4

import pytest

from src.core.video.application.exceptions import (
    MediaNotFound,
    UnsupportedMediaType,
    VideoNotFound,
)
from src.core.video.application.usecases.process_audio_video_media import (
    ProcessAudioVideoMedia,
)
from src.core.video.domain.value_objects import AudioVideoMedia, MediaStatus, MediaType
from src.core.video.domain.video import Video


@pytest.fixture
def mock_repository():
    return Mock()


@pytest.fixture
def use_case(mock_repository):
    return ProcessAudioVideoMedia(repository=mock_repository)


@pytest.fixture
def fake_video():
    video = Mock(spec=Video)
    video.video = Mock(spec=AudioVideoMedia)
    return video


def test_should_process_video_when_media_is_completed(
    use_case, mock_repository, fake_video
):
    video_id = uuid4()
    encoded_location = "/path/encoded.mp4"

    mock_repository.get_by_id.return_value = fake_video

    input_data = ProcessAudioVideoMedia.Input(
        video_id=video_id,
        encoded_location=encoded_location,
        media_status=MediaStatus.COMPLETED,
        media_type=MediaType.VIDEO,
    )

    use_case.execute(input_data)

    fake_video.process.assert_called_once_with(
        status=MediaStatus.COMPLETED, encoded_location=encoded_location
    )
    mock_repository.update.assert_called_once_with(fake_video)


def test_should_mark_video_as_failed(use_case, mock_repository, fake_video):
    video_id = uuid4()

    mock_repository.get_by_id.return_value = fake_video

    input_data = ProcessAudioVideoMedia.Input(
        video_id=video_id,
        encoded_location="/does-not-matter",
        media_status=MediaStatus.ERROR,
        media_type=MediaType.VIDEO,
    )

    use_case.execute(input_data)

    fake_video.process.assert_called_once_with(
        status=MediaStatus.ERROR, encoded_location="/does-not-matter"
    )
    mock_repository.update.assert_called_once_with(fake_video)


def test_should_raise_when_video_not_found(use_case, mock_repository):
    mock_repository.get_by_id.return_value = None

    input_data = ProcessAudioVideoMedia.Input(
        video_id=uuid4(),
        encoded_location="",
        media_status=MediaStatus.COMPLETED,
        media_type=MediaType.VIDEO,
    )

    with pytest.raises(VideoNotFound):
        use_case.execute(input_data)


def test_should_raise_when_video_has_no_media(use_case, mock_repository):
    video = Mock(spec=Video)
    video.video = None
    mock_repository.get_by_id.return_value = video

    input_data = ProcessAudioVideoMedia.Input(
        video_id=uuid4(),
        encoded_location="",
        media_status=MediaStatus.COMPLETED,
        media_type=MediaType.VIDEO,
    )

    with pytest.raises(MediaNotFound):
        use_case.execute(input_data)


def test_should_raise_on_unsupported_media_type(use_case, mock_repository, fake_video):
    mock_repository.get_by_id.return_value = fake_video

    input_data = ProcessAudioVideoMedia.Input(
        video_id=uuid4(),
        encoded_location="/some/path",
        media_status=MediaStatus.COMPLETED,
        media_type=MediaType.TRAILER,
    )

    with pytest.raises(UnsupportedMediaType):
        use_case.execute(input_data)
