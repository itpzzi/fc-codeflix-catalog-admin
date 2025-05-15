import uuid
from unittest.mock import Mock, create_autospec

import pytest

from core.video.domain.video import Video
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository
from src.core.category.domain.category_repository import ICategoryRepository
from src.core.genre.domain.genre_repository import IGenreRepository
from src.core.video.application.exceptions import InvalidVideo, RelatedEntitiesNotFound
from src.core.video.application.usecases.create_video_without_media import (
    CreateVideoWithoutMedia,
)
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
from src.core.video.domain.video_repository import IVideoRepository


@pytest.fixture
def valid_data():
    return dict(
        title="Test Title",
        description="Test Description",
        duration=Duration(150),
        launched_at=LaunchedAt(2023),
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
def mock_category_repository() -> ICategoryRepository:
    repository = create_autospec(ICategoryRepository)
    repository.list.return_value = []
    return repository


@pytest.fixture
def mock_genre_repository() -> IGenreRepository:
    repository = create_autospec(IGenreRepository)
    repository.list.return_value = []
    return repository


@pytest.fixture
def mock_cast_member_repository() -> ICastMemberRepository:
    repository = create_autospec(ICastMemberRepository)
    repository.list.return_value = []
    return repository


@pytest.fixture
def mock_video_repository() -> IVideoRepository:
    repository = create_autospec(IVideoRepository)
    return repository


class TestCreateVideoWithoutMedia:
    def test_should_raise_exception_when_related_objects_not_found(
        self,
        mock_category_repository: ICategoryRepository,
        mock_genre_repository: IGenreRepository,
        mock_cast_member_repository: ICastMemberRepository,
        mock_video_repository: IVideoRepository,
    ):
        input = CreateVideoWithoutMedia.Input(
            title=Title("The Matrix"),
            description=Description("A journey to the Matrix"),
            launched_at=LaunchedAt(2019),
            opened=False,
            duration=Duration(136),
            rating=Rating(Rating.AGE_16),
            categories=Categories({uuid.uuid4()}),
            genres=Genres({uuid.uuid4()}),
            cast_members=CastMembers({uuid.uuid4()}),
        )
        use_case = CreateVideoWithoutMedia(
            video_repository=mock_video_repository,
            category_repository=mock_category_repository,
            genre_repository=mock_genre_repository,
            cast_member_repository=mock_cast_member_repository,
        )
        error_messages = "; ".join(
            [
                "Invalid categories",
                "Invalid genres",
                "Invalid cast members",
            ]
        )

        with pytest.raises(RelatedEntitiesNotFound) as exc:
            use_case.execute(input)

        assert mock_video_repository.save.called is False
        assert str(exc.value) == error_messages

    def test_when_video_data_is_invalid_then_raise_invalid_video(
        self,
        mock_category_repository,
        mock_genre_repository,
        mock_cast_member_repository,
        mock_video_repository,
    ):
        input = CreateVideoWithoutMedia.Input(
            title="",  # inválido
            description=Description("Any"),
            launched_at=LaunchedAt(2020),
            opened=False,
            duration=Duration(100),
            rating=Rating(Rating.AGE_10),
            categories=set(),
            genres=set(),
            cast_members=set(),
        )

        use_case = CreateVideoWithoutMedia(
            video_repository=mock_video_repository,
            category_repository=mock_category_repository,
            genre_repository=mock_genre_repository,
            cast_member_repository=mock_cast_member_repository,
        )

        with pytest.raises(InvalidVideo):
            use_case.execute(input)

        assert mock_video_repository.save.called is False

    def test_should_create_video_when_all_data_is_valid(
        self,
        mock_category_repository,
        mock_genre_repository,
        mock_cast_member_repository,
        mock_video_repository,
    ):
        existing_id = uuid.uuid4()
        related_entity_mock = Mock()
        related_entity_mock.id = existing_id

        mock_category_repository.list.return_value = [related_entity_mock]
        mock_genre_repository.list.return_value = [related_entity_mock]
        mock_cast_member_repository.list.return_value = [related_entity_mock]

        input = CreateVideoWithoutMedia.Input(
            title=Title("Valid"),
            description=Description("Valid"),
            launched_at=LaunchedAt(2020),
            opened=True,
            duration=Duration(150),
            rating=Rating(Rating.AGE_16),
            categories=Categories({existing_id}),
            genres=Genres({existing_id}),
            cast_members=CastMembers({existing_id}),
        )

        use_case = CreateVideoWithoutMedia(
            video_repository=mock_video_repository,
            category_repository=mock_category_repository,
            genre_repository=mock_genre_repository,
            cast_member_repository=mock_cast_member_repository,
        )

        output = use_case.execute(input)

        assert output.id is not None
        mock_video_repository.save.assert_called_once()
