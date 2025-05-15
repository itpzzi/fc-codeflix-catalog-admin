from dataclasses import dataclass
from typing import Set
from uuid import UUID

from src.core._shared.notification import Notification
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository
from src.core.category.domain.category_repository import ICategoryRepository
from src.core.genre.domain.genre_repository import IGenreRepository
from src.core.video.application.exceptions import InvalidVideo, RelatedEntitiesNotFound
from src.core.video.domain.value_objects import (
    CastMembers,
    Categories,
    Description,
    Duration,
    Genres,
    LaunchedAt,
    Rating,
    Title,
)
from src.core.video.domain.video import Video
from src.core.video.domain.video_repository import IVideoRepository


class CreateVideoWithoutMedia:
    @dataclass
    class Input:
        title: Title
        description: Description
        launched_at: LaunchedAt
        opened: bool
        duration: Duration
        rating: Rating
        categories: Categories
        genres: Genres
        cast_members: CastMembers

    @dataclass
    class Output:
        id: UUID

    def __init__(
        self,
        video_repository: IVideoRepository,
        category_repository: ICategoryRepository,
        genre_repository: IGenreRepository,
        cast_member_repository: ICastMemberRepository,
    ):
        self._video_repository = video_repository
        self._category_repository = category_repository
        self._genre_repository = genre_repository
        self._cast_member_repository = cast_member_repository
        self._notification: Notification = Notification()

    def execute(self, input: Input) -> Output:
        self._validate_related_entities(input)
        self._raise_if_invalid_entities()
        video = self._create_video_or_raise(input)
        self._video_repository.save(video)
        return self.Output(id=video.id)

    def _validate_related_entities(self, input: Input):
        self._validate_related(
            input_ids=input.categories,
            existing_ids={e.id for e in self._category_repository.list()},
            message="Invalid categories",
        )

        self._validate_related(
            input_ids=input.genres,
            existing_ids={e.id for e in self._genre_repository.list()},
            message="Invalid genres",
        )

        self._validate_related(
            input_ids=input.cast_members,
            existing_ids={e.id for e in self._cast_member_repository.list()},
            message="Invalid cast members",
        )

    def _raise_if_invalid_entities(self):
        if self._notification.has_errors:
            raise RelatedEntitiesNotFound(self._notification.messages)

    def _create_video_or_raise(self, input: Input) -> Video:
        try:
            return Video(
                title=input.title,
                description=input.description,
                launched_at=input.launched_at,
                opened=input.opened,
                duration=input.duration,
                rating=input.rating,
                categories=input.categories,
                genres=input.genres,
                cast_members=input.cast_members,
            )
        except ValueError as err:
            raise InvalidVideo(str(err))

    def _validate_related(
        self,
        input_ids: Set[UUID],
        existing_ids: Set[UUID],
        message: str,
    ):
        if not input_ids.issubset(existing_ids):
            self._notification.add_error(message)
