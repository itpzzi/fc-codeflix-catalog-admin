import uuid
import pytest

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
from src.core.genre.application.usecases.update_genre import (
    UpdateGenreInput,
    UpdateGenreUseCase,
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
    empty_category_repository,
    movie_category,
    documentary_category,
) -> ICategoryRepository:
    empty_category_repository.save(movie_category)
    empty_category_repository.save(documentary_category)
    return empty_category_repository


@pytest.fixture
def existing_genre() -> Genre:
    return Genre(name="Old Genre", is_active=False)


# -------------------- Testes de atualização -------------------- #


class TestUpdateGenreIntegration:

    def test_when_provided_categories_do_not_exist_then_raise_related_categories_not_found(
        self,
        empty_category_repository,
        genre_repository,
        existing_genre,
    ):
        genre_repository.save(existing_genre)
        use_case = UpdateGenreUseCase(
            repository=genre_repository,
            category_repository=empty_category_repository,
        )

        fake_category_id = uuid.uuid4()

        with pytest.raises(RelatedCategoriesNotFound) as exc:
            use_case.execute(
                UpdateGenreInput(
                    id=existing_genre.id,
                    name="Updated",
                    categories={fake_category_id},
                    is_active=True,
                )
            )

        assert str(fake_category_id) in str(exc.value)

    def test_when_updated_genre_is_invalid_then_raise_invalid_genre(
        self,
        category_repository_with_categories,
        genre_repository,
        existing_genre,
    ):
        genre_repository.save(existing_genre)

        use_case = UpdateGenreUseCase(
            repository=genre_repository,
            category_repository=category_repository_with_categories,
        )

        with pytest.raises(InvalidGenre, match="name cannot be empty"):
            use_case.execute(
                UpdateGenreInput(
                    id=existing_genre.id,
                    name="",
                    categories=set(),
                    is_active=True,
                )
            )

    def test_when_genre_is_valid_then_it_is_updated(
        self,
        genre_repository,
        category_repository_with_categories,
        movie_category,
        documentary_category,
        existing_genre,
    ):
        genre_repository.save(existing_genre)

        use_case = UpdateGenreUseCase(
            repository=genre_repository,
            category_repository=category_repository_with_categories,
        )

        request = UpdateGenreInput(
            id=existing_genre.id,
            name="Updated Genre",
            categories={movie_category.id, documentary_category.id},
            is_active=True,
        )

        use_case.execute(request)

        updated_genre = genre_repository.get_by_id(existing_genre.id)
        assert updated_genre is not None
        assert updated_genre.name == "Updated Genre"
        assert updated_genre.is_active is True
        assert updated_genre.categories == {movie_category.id, documentary_category.id}
