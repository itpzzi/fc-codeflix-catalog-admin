import uuid
from unittest.mock import create_autospec

import pytest

from src.core.genre.application.usecases.list_genre import (
    ListGenre,
    ListGenreItem,
)
from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import IGenreRepository

# ------------------------- Fixtures ------------------------- #


@pytest.fixture
def movie_category() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def documentary_category() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def mock_genre_repository() -> IGenreRepository:
    return create_autospec(IGenreRepository)


@pytest.fixture
def genre_list(movie_category, documentary_category):
    return [
        Genre(name="Terror", categories={movie_category}, is_active=True),
        Genre(name="Ação", categories={documentary_category}, is_active=False),
        Genre(name="Comédia", categories={}, is_active=True),
        Genre(
            name="Drama",
            categories={movie_category, documentary_category},
            is_active=True,
        ),
    ]


@pytest.fixture
def mock_repo_with_genres(mock_genre_repository, genre_list):
    mock_genre_repository.list.return_value = genre_list
    return mock_genre_repository


# ------------------------- Testes --------------------------- #


class TestListGenre:
    def test_list_all_genres(self, mock_repo_with_genres, genre_list):
        input = ListGenre.Input(per_page=4)
        use_case = ListGenre(repository=mock_repo_with_genres)

        expected_data = [
            ListGenreItem(
                id=g.id,
                name=g.name,
                categories=g.categories,
                is_active=g.is_active,
            )
            for g in genre_list
        ]

        output = use_case.execute(input)

        assert output.data == sorted(expected_data, key=lambda x: x.name)
        assert output.meta.total == 4
        assert output.meta.current_page == 1
        assert output.meta.per_page == 4

    def test_empty_repository(self, mock_genre_repository):
        mock_genre_repository.list.return_value = []
        input = ListGenre.Input()
        use_case = ListGenre(repository=mock_genre_repository)

        output = use_case.execute(input)

        assert output.data == []
        assert output.meta.total == 0
        assert output.meta.current_page == 1
        assert output.meta.per_page == 2

    @pytest.mark.parametrize(
        "order_by, reverse, current_page, per_page, expected_names",
        [
            ("name", False, 1, 2, ["Ação", "Comédia"]),
            ("name", False, 2, 2, ["Drama", "Terror"]),
            ("name", True, 1, 2, ["Terror", "Drama"]),
            ("name", True, 2, 2, ["Comédia", "Ação"]),
        ],
    )
    def test_ordering_and_pagination(
        self,
        mock_repo_with_genres,
        genre_list,
        order_by,
        reverse,
        current_page,
        per_page,
        expected_names,
    ):
        input = ListGenre.Input(
            order_by=order_by,
            reverse=reverse,
            current_page=current_page,
            per_page=per_page,
        )
        use_case = ListGenre(repository=mock_repo_with_genres)

        sorted_data = sorted(
            genre_list,
            key=lambda g: getattr(g, order_by),
            reverse=reverse,
        )
        paged_data = sorted_data[
            (current_page - 1) * per_page : current_page * per_page
        ]
        expected_data = [
            ListGenreItem(
                id=g.id,
                name=g.name,
                categories=g.categories,
                is_active=g.is_active,
            )
            for g in paged_data
        ]

        output = use_case.execute(input)

        assert [g.name for g in output.data] == expected_names
        assert output.data == expected_data
        assert output.meta.total == len(genre_list)
        assert output.meta.current_page == current_page
        assert output.meta.per_page == per_page
