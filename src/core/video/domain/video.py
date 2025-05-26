from dataclasses import dataclass, field
from uuid import UUID

from src.core._shared.common_types import Location
from src.core._shared.domain.entity import Entity
from src.core.video.domain.events.domain_events import AudioVideoMediaUpdatedEvent
from src.core.video.domain.value_objects import (
    AudioVideoMedia,
    CastMembers,
    Categories,
    Description,
    Duration,
    Genres,
    ImageMedia,
    LaunchYear,
    MediaStatus,
    MediaType,
    Rating,
    Title,
)


@dataclass(kw_only=True, slots=True)
class Video(Entity):
    title: Title
    description: Description
    duration: Duration
    launch_year: LaunchYear
    rating: Rating
    opened: bool
    published: bool = field(default=False, init=False)

    categories: Categories
    genres: Genres
    cast_members: CastMembers

    banner: ImageMedia | None = None
    thumbnail: ImageMedia | None = None
    thumbnail_half: ImageMedia | None = None
    trailer: AudioVideoMedia | None = None
    video: AudioVideoMedia | None = None

    def process(self, status: MediaStatus, encoded_location: Location):
        if status == MediaStatus.COMPLETED:
            self.video = self.video.complete(encoded_location=encoded_location)
            self.publish()
        else:
            self.video = self.video.fail()

        self.validate()

    def publish(self):
        if not isinstance(self.video, AudioVideoMedia):
            self.notification.add_error("video should be set before publishing")
        elif self.video.status != MediaStatus.COMPLETED:
            self.notification.add_error("video should be completed before publishing")

        if not self.notification.has_errors:
            self._update_field("published", True)

    def validate(self):
        self._validate_value_object("title", Title, ValueError)
        self._validate_value_object("description", Description, ValueError)
        self._validate_value_object("duration", Duration, (ValueError, TypeError))
        self._validate_value_object("launch_year", LaunchYear, (ValueError, TypeError))
        self._validate_rating()

        self._validate_primitive_type("opened", bool)
        self._validate_primitive_type("published", bool)

        self._validate_value_object("categories", Categories, TypeError)
        self._validate_value_object("genres", Genres, TypeError)
        self._validate_value_object("cast_members", CastMembers, TypeError)
        self._check_notification_has_errors()

    def _validate_value_object(self, field_name: str, constructor, expected_exception):
        value = getattr(self, field_name)
        try:
            constructor(value)
        except expected_exception as error:
            self.notification.add_error(str(error))

    def _validate_primitive_type(self, field_name: str, expected_type: type):
        value = getattr(self, field_name)
        if not isinstance(value, expected_type):
            self.notification.add_error(
                f"{field_name} must be a {expected_type.__name__}"
            )

    def _validate_rating(self):
        value = getattr(self, "rating")
        if not isinstance(value, Rating):
            self.notification.add_error("rating must be a valid Rating")

    def _update_field(self, field_name: str, value):
        setattr(self, field_name, value)
        self.validate()

    def update_title(self, value: Title):
        self._update_field("title", value)

    def update_description(self, value: Description):
        self._update_field("description", value)

    def update_duration(self, value: Duration):
        self._update_field("duration", value)

    def update_launch_year(self, value: LaunchYear):
        self._update_field("launch_year", value)

    def update_rating(self, value: Rating):
        self._update_field("rating", value)

    def update_opened(self, value: bool):
        self._update_field("opened", value)

    def add_category(self, value: UUID):
        new_set = Categories(self.categories | {value})
        self._update_field("categories", new_set)

    def add_genre(self, value: UUID):
        new_set = Genres(self.genres | {value})
        self._update_field("genres", new_set)

    def add_cast_member(self, value: UUID):
        new_set = CastMembers(self.cast_members | {value})
        self._update_field("cast_members", new_set)

    def update_banner(self, value: ImageMedia | None):
        self._update_field("banner", value)

    def update_thumbnail(self, value: ImageMedia | None):
        self._update_field("thumbnail", value)

    def update_thumbnail_half(self, value: ImageMedia | None):
        self._update_field("thumbnail_half", value)

    def update_trailer(self, value: AudioVideoMedia | None):
        self._update_field("trailer", value)

    def update_video(self, value: AudioVideoMedia | None):
        self._update_field("video", value)
        self.dispatch(
            AudioVideoMediaUpdatedEvent(
                aggregate_id=self.id,
                full_path=value.raw_location,
                media_type=MediaType.VIDEO,
            )
        )

    def __repr__(self):
        return f"<Video {self.title} ({self.launch_year}) - {self.id}>"

    def __str__(self):
        return f"{self.title} ({self.launch_year}) - {self.description}"
