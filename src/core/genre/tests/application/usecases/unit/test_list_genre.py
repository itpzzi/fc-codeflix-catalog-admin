

from unittest.mock import create_autospec
import uuid
import pytest
from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import ICategoryRepository
from src.core.category.infra.in_memory_category_repository import InMemoryCategoryRepository
from src.core.genre.application.usecases.list_genre import (
    GenreOutput,
    ListGenreRequest,
    ListGenreResponse,
    ListGenreUseCase,
)
from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import IGenreRepository


# ------------------------- Fixtures ------------------------ #

@pytest.fixture
def mock_genre_repository() -> IGenreRepository:
    return create_autospec(IGenreRepository)

@pytest.fixture
def movie_category() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def documentary_category() -> uuid.UUID:
    return uuid.uuid4()


# -------------------- Testes de listagem -------------------- #


class TestListGenre:
    def test_list_genres_with_associated_categories(
        self,
        movie_category,
        documentary_category,
        mock_genre_repository,
    ):
        categories_ids = {movie_category, documentary_category}
        request = ListGenreRequest()
        use_case = ListGenreUseCase(
            repository=mock_genre_repository,
        )
        genre_fantasy = Genre(name="Fantasy", categories=categories_ids)
        genre_drama = Genre(name="Drama", categories={})
        mock_genre_repository.list.return_value = [genre_fantasy, genre_drama]

        response = use_case.execute(request)

        assert len(response.data) == 2
        assert response == ListGenreResponse(data=response.data)
        assert response == ListGenreResponse(
            data=[
                GenreOutput(
                    id=genre_fantasy.id,
                    name=genre_fantasy.name,
                    categories=genre_fantasy.categories,
                    is_active=genre_fantasy.is_active,
                ),
                GenreOutput(
                    id=genre_drama.id,
                    name=genre_drama.name,
                    categories={},
                    is_active=genre_drama.is_active,
                ),
            ]
        )

    def test_return_empty_list_when_no_genre_exists(
        self,
        mock_genre_repository,
    ):
        request = ListGenreRequest()
        use_case = ListGenreUseCase(
            repository=mock_genre_repository,
        )

        response = use_case.execute(request)

        assert len(response.data) == 0
        assert response == ListGenreResponse(data=response.data)
        assert response == ListGenreResponse(data=[])
