import uuid

import pytest

from src.core.video.domain.value_objects import AudioVideoMedia, MediaStatus, Rating
from src.core.video.domain.video import Video
from src.django_project.video_app.mapper import parse_media_status_enum
from src.django_project.video_app.models import Video as VideoModel
from src.django_project.video_app.repository import DjangoORMVideoRepository


@pytest.fixture
def video_repository():
    return DjangoORMVideoRepository()


@pytest.fixture
def sample_video():
    return Video(
        title="Sample Video",
        description="Description",
        duration=90,
        launch_year=2024,
        rating=Rating.L,
        opened=True,
        categories=set(),
        genres=set(),
        cast_members=set(),
    )


@pytest.fixture
def saved_video(video_repository, sample_video):
    video_repository.save(sample_video)
    return sample_video


@pytest.mark.django_db
class TestSave:
    def test_can_save_video(self, video_repository, sample_video):
        assert len(video_repository.list()) == 0
        video_repository.save(sample_video)
        assert len(video_repository.list()) == 1

        saved = video_repository.get_by_id(sample_video.id)
        assert saved is not None
        assert saved.id == sample_video.id
        assert saved.title == sample_video.title
        assert saved.description == sample_video.description
        assert saved.rating == sample_video.rating


@pytest.mark.django_db
class TestGet:
    def test_can_get_by_id(self, video_repository, saved_video):
        found = video_repository.get_by_id(saved_video.id)
        assert found is not None
        assert found.id == saved_video.id

    def test_return_none_for_nonexistent_id(self, video_repository):
        fake_id = uuid.uuid4()
        assert video_repository.get_by_id(fake_id) is None


@pytest.mark.django_db
class TestDelete:
    def test_can_delete_video(self, video_repository, saved_video):
        assert len(video_repository.list()) == 1
        video_repository.delete(saved_video.id)
        assert video_repository.get_by_id(saved_video.id) is None
        assert len(video_repository.list()) == 0


@pytest.mark.django_db
class TestUpdate:
    def test_can_update_video(self, video_repository, saved_video):
        found = video_repository.get_by_id(saved_video.id)
        assert found is not None
        assert found.video is None

        updated = Video(
            id=saved_video.id,
            title="Updated Title",
            description="Updated Description",
            duration=120,
            launch_year=2025,
            rating=Rating.AGE_16,
            opened=False,
            categories=set(),
            genres=set(),
            cast_members=set(),
            video=AudioVideoMedia(
                name="Ghost",
                raw_location="/tmp/ghost.mp4",
                encoded_location="/tmp/ghost.mp4",
                status=MediaStatus.PENDING,
            ),
        )
        video_repository.update(updated)
        found = video_repository.get_by_id(saved_video.id)

        assert found is not None
        assert found.title == "Updated Title"
        assert found.description == "Updated Description"
        assert found.duration == 120
        assert found.rating == Rating.AGE_16
        assert found.launch_year == 2025
        assert found.opened is False
        assert found.published is False
        assert found.categories == set()
        assert found.genres == set()
        assert found.cast_members == set()

        video_model = VideoModel.objects.filter(id=saved_video.id).first()

        assert video_model.video is not None
        assert video_model.video.name == "Ghost"
        assert video_model.video.raw_location == "/tmp/ghost.mp4"
        assert video_model.video.encoded_location == "/tmp/ghost.mp4"
        assert parse_media_status_enum(video_model.video.status) == MediaStatus.PENDING

    def test_update_nonexistent_video_does_nothing(self, video_repository):
        fake = Video(
            id=uuid.uuid4(),
            title="Ghost",
            description="Nope",
            duration=1,
            launch_year=2022,
            rating=Rating.L,
            opened=False,
            categories=set(),
            genres=set(),
            cast_members=set(),
        )
        video_repository.update(fake)
        assert video_repository.get_by_id(fake.id) is None
        assert len(video_repository.list()) == 0


@pytest.mark.django_db
class TestList:
    def test_list_all_videos(self, video_repository, saved_video):
        videos = video_repository.list()
        assert len(videos) == 1
        assert saved_video.id in [v.id for v in videos]

    def test_returns_empty_list_when_no_videos(self, video_repository):
        assert video_repository.list() == []
