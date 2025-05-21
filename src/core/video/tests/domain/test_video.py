import uuid
from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from src.core._shared.domain.entity import Entity
from src.core.video.domain.events.domain_events import AudioVideoMediaUpdatedEvent
from src.core.video.domain.value_objects import (
    AudioVideoMedia,
    Duration,
    ImageMedia,
    LaunchYear,
    MediaStatus,
    MediaType,
    Rating,
)
from src.core.video.domain.video import Video


@pytest.fixture
def valid_data():
    return dict(
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


@pytest.fixture
def mock_validate():
    with patch.object(Video, "validate") as mock:
        yield mock


@pytest.fixture
def mock_publish():
    with patch.object(Video, "publish") as mock:
        yield mock


class TestVideoInitialization:
    def test_video_should_be_created_with_all_required_fields(self, valid_data):
        video = Video(**valid_data)
        assert video.title == "Test Title"
        assert video.description == "Test Description"
        assert video.duration == Duration(150)
        assert video.launch_year == LaunchYear(2023)
        assert video.rating == Rating(Rating.AGE_10)
        assert video.opened is True
        assert video.categories == set()
        assert video.genres == set()
        assert video.cast_members == set()

    def test_video_should_call_validate_after_initialization(
        self, valid_data, mock_validate
    ):
        Video(**valid_data)
        mock_validate.assert_called_once()

    def test_video_should_have_default_published_as_false(self, valid_data):
        with pytest.raises(TypeError) as exc:
            Video(**valid_data, published=False)
        assert "got an unexpected keyword argument 'published'" in str(exc.value)

    def test_video_should_enforce_kw_only_construction(self):
        with pytest.raises(TypeError, match="takes 1 positional argument but"):
            Video("Test Title", "Test Description")

    def test_video_should_belong_to_entity_base_class(self):
        assert issubclass(Video, Entity)


class TestVideoUpdate:
    @pytest.mark.parametrize(
        "update_method,update_value",
        [
            ("update_title", "New Title"),
            ("update_description", "New Description"),
            ("update_duration", Duration(70)),
            ("update_launch_year", LaunchYear(1997)),
            ("update_rating", Rating(Rating.AGE_18)),
            ("update_opened", True),
            ("add_category", uuid.uuid4()),
            ("add_genre", uuid.uuid4()),
            ("add_cast_member", uuid.uuid4()),
        ],
    )
    def test_video_should_call_validate_on_update(
        self, valid_video, mock_validate, update_method, update_value
    ):
        getattr(valid_video, update_method)(update_value)
        mock_validate.assert_called_once()

    @pytest.mark.parametrize(
        "attr,update_method,dummy_value",
        [
            ("banner", "update_banner", ImageMedia),
            ("thumbnail", "update_thumbnail", ImageMedia),
            ("thumbnail_half", "update_thumbnail_half", ImageMedia),
            ("video", "update_video", AudioVideoMedia),
            ("trailer", "update_trailer", AudioVideoMedia),
        ],
    )
    def test_video_should_update_media_fields_and_validate(
        self, valid_video, mock_validate, attr, update_method, dummy_value
    ):
        if dummy_value is ImageMedia:
            dummy_instance = dummy_value(name=None, location=None)
        elif dummy_value is AudioVideoMedia:
            dummy_instance = dummy_value(
                name=None,
                raw_location=None,
                encoded_location=None,
                status=None,
                media_type=None,
            )

        method = getattr(valid_video, update_method)
        method(dummy_instance)

        assert getattr(valid_video, attr) is dummy_instance
        mock_validate.assert_called_once()

    def test_video_should_update_video_and_dispatch_update_event(self, valid_video):
        media = AudioVideoMedia(
            name="test",
            raw_location="/tmp/test.mp4",
            encoded_location="/tmp/test.mp4",
            status=MediaStatus.PENDING,
            media_type=MediaType.VIDEO,
        )
        valid_video.update_video(media)
        assert valid_video.video == media
        assert len(valid_video.events) == 1
        assert valid_video.events == [
            AudioVideoMediaUpdatedEvent(
                aggregate_id=valid_video.id,
                full_path="/tmp/test.mp4",
                media_type=MediaType.VIDEO,
            )
        ]


class TestVideoPublishing:
    def test_video_should_require_a_video_to_be_published(self, valid_video):
        video_without_media = valid_video

        video_without_media.publish()

        assert not video_without_media.published
        assert video_without_media.notification.has_errors
        assert (
            "video should be set before publishing"
            in video_without_media.notification.messages
        )

    @pytest.mark.parametrize(
        "status", [MediaStatus.PENDING, MediaStatus.PROCESSING, MediaStatus.ERROR]
    )
    def test_video_should_not_publish_if_video_status_is_invalid(
        self, valid_video, status
    ):
        mock_video = Mock(spec=AudioVideoMedia)
        mock_video.status = status
        valid_video.video = mock_video

        valid_video.publish()

        assert not valid_video.published
        assert valid_video.notification.has_errors
        assert (
            "video should be completed before publishing"
            in valid_video.notification.messages
        )

    def test_video_should_publish_if_video_status_is_completed(self, valid_video):
        mock_video = Mock(spec=AudioVideoMedia)
        mock_video.status = MediaStatus.COMPLETED
        valid_video.video = mock_video

        valid_video.publish()

        assert valid_video.published is True


class TestVideoRequiredFields:
    @pytest.mark.parametrize(
        "field,invalid_value,error_message",
        [
            ("title", "", "title cannot be empty"),
            ("description", "", "description cannot be empty"),
            ("duration", -1, "duration must be a positive number"),
            ("launch_year", 1899, "launch year must be between 1900 and 2100"),
            ("rating", "INVALID", ""),
            ("opened", None, "opened must be a bool"),
            ("categories", ["not", "uuids"], "Categories must be a set"),
            ("categories", {123}, "all items in Categories must be UUIDs"),
            ("genres", "not_a_set", "Genres must be a set"),
            ("genres", {123}, "all items in Genres must be UUIDs"),
            ("cast_members", None, "CastMembers must be a set"),
            ("cast_members", {0}, "all items in CastMembers must be UUIDs"),
        ],
    )
    def test_video_should_require_valid_fields(
        self, valid_data, field, invalid_value, error_message
    ):
        invalid_data = valid_data.copy()
        invalid_data[field] = invalid_value
        with pytest.raises(
            (ValueError, TypeError), match=error_message if error_message else ""
        ):
            Video(**invalid_data)

    def test_video_should_store_duration_as_decimal(self, valid_data):
        video = Video(**valid_data)
        assert isinstance(video.duration, Decimal)


class TestVideoValidation:
    def test_video_should_accumulate_validation_errors_in_notification(
        self, valid_data
    ):
        invalid_data = {
            **valid_data,
            "title": "",
            "launch_year": 1200,
            "duration": -1,
        }
        with pytest.raises(ValueError) as exc:
            Video(**invalid_data)
        assert "title cannot be empty" in str(exc.value)
        assert "duration must be a positive number" in str(exc.value)
        assert "launch year must be between 1900 and 2100" in str(exc.value)


class TestVideoDunderBehavior:
    def test_video_should_not_allow_dynamic_attribute_assignment_due_to_slots(
        self, valid_data
    ):
        video = Video(**valid_data)
        with pytest.raises(AttributeError):
            video.foo = "bar"
