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
def video_repository() -> IVideoRepository:

    from src.core.video.infra.in_memory_video_repository import InMemoryVideoRepository

    return InMemoryVideoRepository()


@pytest.fixture
def use_case(video_repository):
    return ProcessAudioVideoMedia(repository=video_repository)


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
def video_with_media(valid_video) -> Video:
    media = AudioVideoMedia(
        name="test.mp4",
        raw_location="/tmp/test.mp4",
        encoded_location="",
        status=MediaStatus.PENDING,
        media_type=MediaType.VIDEO,
    )
    valid_video.update_video(media)
    return valid_video


def test_should_process_video_completed(use_case, video_repository, video_with_media):
    video_repository.save(video_with_media)
    video_id = video_with_media.id
    encoded_location = "/encoded/video.mp4"

    input_data = ProcessAudioVideoMedia.Input(
        video_id=video_id,
        encoded_location=encoded_location,
        media_status=MediaStatus.COMPLETED,
        media_type=MediaType.VIDEO,
    )

    use_case.execute(input_data)

    updated = video_repository.get_by_id(video_id)
    assert updated.video.status == MediaStatus.COMPLETED
    assert updated.video.encoded_location == encoded_location
    assert updated.published is True


def test_should_process_failed_video(use_case, video_repository, video_with_media):
    video_repository.save(video_with_media)
    video_id = video_with_media.id

    input_data = ProcessAudioVideoMedia.Input(
        video_id=video_id,
        encoded_location="/any/path.mp4",
        media_status=MediaStatus.ERROR,
        media_type=MediaType.VIDEO,
    )

    use_case.execute(input_data)

    updated = video_repository.get_by_id(video_id)
    assert updated.video.status == MediaStatus.ERROR
    assert updated.video.encoded_location == ""
    assert updated.published is False


def test_should_raise_if_video_not_found(use_case):
    input_data = ProcessAudioVideoMedia.Input(
        video_id=uuid4(),
        encoded_location="/unused",
        media_status=MediaStatus.COMPLETED,
        media_type=MediaType.VIDEO,
    )

    with pytest.raises(VideoNotFound):
        use_case.execute(input_data)


def test_should_raise_if_video_has_no_media(use_case, video_repository, valid_video):
    video_repository.save(valid_video)

    input_data = ProcessAudioVideoMedia.Input(
        video_id=valid_video.id,
        encoded_location="/unused",
        media_status=MediaStatus.COMPLETED,
        media_type=MediaType.VIDEO,
    )

    with pytest.raises(MediaNotFound):
        use_case.execute(input_data)


def test_should_raise_if_media_type_is_trailer(
    use_case, video_repository, video_with_media
):
    video_repository.save(video_with_media)

    input_data = ProcessAudioVideoMedia.Input(
        video_id=video_with_media.id,
        encoded_location="/encoded.mp4",
        media_status=MediaStatus.COMPLETED,
        media_type=MediaType.TRAILER,
    )

    with pytest.raises(UnsupportedMediaType):
        use_case.execute(input_data)
