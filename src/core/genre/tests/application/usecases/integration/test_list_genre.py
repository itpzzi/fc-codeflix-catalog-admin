# -------------------- Fixtures -------------------- #


import pytest

from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import ICategoryRepository
from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)
from src.core.genre.application.usecases.list_genre import (
    ListGenre,
    ListGenreItem,
)
from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import IGenreRepository
from src.core.genre.infra.in_memory_genre_repository import InMemoryGenreRepository


@pytest.fixture
def genre_repository() -> IGenreRepository:
    return InMemoryGenreRepository()


@pytest.fixture
def empty_category_repository() -> ICategoryRepository:
    return InMemoryCategoryRepository()


@pytest.fixture
def movie_category() -> Category:
    return Category(name="Movie")


@pytest.fixture
def documentary_category() -> Category:
    return Category(name="Documentary")


@pytest.fixture
def category_repository_with_categories(
    empty_category_repository, movie_category, documentary_category
) -> ICategoryRepository:
    empty_category_repository.save(movie_category)
    empty_category_repository.save(documentary_category)
    return empty_category_repository


# -------------------- Testes de listagem -------------------- #


class TestListGenre:
    def test_list_genres_with_associated_categories(
        self,
        category_repository_with_categories,
        genre_repository,
    ):
        categories_ids = {
            category.id for category in category_repository_with_categories.list()
        }
        input = ListGenre.Input()
        use_case = ListGenre(
            repository=genre_repository,
        )
        genre_fantasy = Genre(name="Fantasy", categories=categories_ids)
        genre_drama = Genre(name="Drama", categories={})
        genre_repository.save(genre_fantasy)
        genre_repository.save(genre_drama)

        output = use_case.execute(input=input)

        assert len(output.data) == 2
        assert output == ListGenre.Output(data=output.data)
        assert output == ListGenre.Output(
            data=[
                ListGenreItem(
                    id=genre_fantasy.id,
                    name=genre_fantasy.name,
                    categories=genre_fantasy.categories,
                    is_active=genre_fantasy.is_active,
                ),
                ListGenreItem(
                    id=genre_drama.id,
                    name=genre_drama.name,
                    categories={},
                    is_active=genre_drama.is_active,
                ),
            ]
        )

    def test_return_empty_list_when_no_genre_exists(
        self,
        genre_repository,
    ):
        input = ListGenre.Input()
        use_case = ListGenre(
            repository=genre_repository,
        )

        output = use_case.execute(input=input)

        assert len(output.data) == 0
        assert output == ListGenre.Output(data=output.data)
        assert output == ListGenre.Output(data=[])
