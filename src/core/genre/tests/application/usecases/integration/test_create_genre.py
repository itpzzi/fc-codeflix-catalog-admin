import uuid
from uuid import UUID
import pytest
from unittest.mock import MagicMock, create_autospec

from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import ICategoryRepository
from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import IGenreRepository
from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)
from src.core.genre.infra.in_memory_genre_repository import InMemoryGenreRepository
from src.core.genre.application.exceptions import (
    InvalidGenre,
    RelatedCategoriesNotFound,
)
from src.core.genre.application.usecases.create_genre import (
    CreateGenre,
)

# -------------------- Fixtures -------------------- #


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


# -------------------- Testes de criação -------------------- #


class TestCreateGenre:
    def test_when_provided_categories_do_not_exist_then_raise_related_categories_not_found(
        self,
        empty_category_repository,
        genre_repository,
    ):
        use_case = CreateGenre(
            repository=genre_repository,
            category_repository=empty_category_repository,
        )

        with pytest.raises(
            RelatedCategoriesNotFound, match="Categories with provided IDs not found: "
        ) as exc:
            category_id = uuid.uuid4()
            use_case.execute(
                CreateGenre.Input(
                    name="Genre 1",
                    categories={category_id},
                )
            )

        assert str(category_id) in str(exc.value)

    def test_when_created_genre_is_invalid_then_raise_invalid_genre(
        self,
        documentary_category,
        movie_category,
        category_repository_with_categories,
        genre_repository,
    ) -> None:
        use_case = CreateGenre(
            repository=genre_repository,
            category_repository=category_repository_with_categories,
        )

        # InvalidGenre (application), not ValueError (domain)
        with pytest.raises(InvalidGenre, match="name cannot be empty"):
            use_case.execute(
                CreateGenre.Input(
                    name="",
                    categories={documentary_category.id, movie_category.id},
                )
            )

    def test_when_created_genre_is_valid_and_categories_exist_then_save_genre(
        self,
        documentary_category,
        movie_category,
        category_repository_with_categories,
        genre_repository,
    ):
        use_case = CreateGenre(
            repository=genre_repository,
            category_repository=category_repository_with_categories,
        )

        output = use_case.execute(
            CreateGenre.Input(
                name="Romance",
                categories={documentary_category.id, movie_category.id},
            )
        )

        created_genre = genre_repository.get_by_id(output.id)
        assert output == CreateGenre.Output(id=output.id)
        assert created_genre is not None
        assert created_genre.name == "Romance"
        assert len(created_genre.categories) == 2
        assert created_genre.is_active is True

    def test_create_genre_without_categories(
        self,
        genre_repository,
        category_repository_with_categories,
    ):
        use_case = CreateGenre(
            repository=genre_repository,
            category_repository=category_repository_with_categories,
        )

        output = use_case.execute(
            CreateGenre.Input(
                name="Romance",
            )
        )

        created_genre = genre_repository.get_by_id(output.id)
        assert output == CreateGenre.Output(id=output.id)
        assert created_genre is not None
        assert created_genre.name == "Romance"
        assert len(created_genre.categories) == 0
        assert created_genre.categories == set()
        assert created_genre.is_active is True
