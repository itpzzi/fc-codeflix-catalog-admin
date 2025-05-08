import uuid
from typing import Set
from unittest.mock import create_autospec

import pytest

from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import ICategoryRepository
from src.core.genre.application.exceptions import (
    GenreNotFound,
    InvalidGenre,
    RelatedCategoriesNotFound,
)
from src.core.genre.application.usecases.update_genre import (
    UpdateGenreRequest,
    UpdateGenreUseCase,
)
from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import IGenreRepository


@pytest.fixture
def mock_genre_repository() -> IGenreRepository:
    return create_autospec(IGenreRepository)


@pytest.fixture
def mock_category_repository() -> ICategoryRepository:
    return create_autospec(ICategoryRepository)


@pytest.fixture
def use_case(
    mock_genre_repository: IGenreRepository,
    mock_category_repository: ICategoryRepository,
) -> UpdateGenreUseCase:
    return UpdateGenreUseCase(
        repository=mock_genre_repository,
        category_repository=mock_category_repository,
    )


@pytest.fixture
def mock_empty_category_repository() -> ICategoryRepository:
    repository = create_autospec(ICategoryRepository)
    repository.list.return_value = []
    return repository


class TestUpdateGenreUseCase:

    def test_should_raise_when_genre_not_found(
        self,
        mock_genre_repository: IGenreRepository,
        use_case: UpdateGenreUseCase,
    ) -> None:
        genre_id = uuid.uuid4()
        request = UpdateGenreRequest(
            id=genre_id, name="Terror", categories=set(), is_active=True
        )
        mock_genre_repository.get_by_id.return_value = None

        with pytest.raises(GenreNotFound) as exc:
            use_case.execute(request)

        mock_genre_repository.update.assert_not_called()
        assert (
            str(exc.value) == f"Cannot update non-existent genre. {genre_id} not found"
        )

    def test_should_raise_when_related_categories_not_found(
        self,
        mock_genre_repository: IGenreRepository,
        mock_empty_category_repository: ICategoryRepository,
    ) -> None:
        use_case = UpdateGenreUseCase(
            repository=mock_genre_repository,
            category_repository=mock_empty_category_repository,
        )

        genre_id = uuid.uuid4()
        nonexistent_category_id = uuid.uuid4()

        request = UpdateGenreRequest(
            id=genre_id,
            name="Terror",
            categories={nonexistent_category_id},
            is_active=True,
        )

        with pytest.raises(RelatedCategoriesNotFound) as exc:
            use_case.execute(request)

        assert str(nonexistent_category_id) in str(exc.value)

    def test_should_raise_when_invalid_genre_data(
        self,
        mock_genre_repository: IGenreRepository,
        mock_category_repository: ICategoryRepository,
    ) -> None:
        use_case = UpdateGenreUseCase(
            repository=mock_genre_repository,
            category_repository=mock_category_repository,
        )

        genre_id = uuid.uuid4()
        mock_genre_repository.get_by_id.return_value = Genre(
            name="Initial", is_active=True, categories=set()
        )

        invalid_requests: list[UpdateGenreRequest] = [
            UpdateGenreRequest(id=genre_id, name="", categories=set(), is_active=True),
            UpdateGenreRequest(
                id=genre_id, name="a" * 256, categories=set(), is_active=True
            ),
            UpdateGenreRequest(id=genre_id, name="", categories=set(), is_active="invalid"),  # type: ignore
        ]

        for request in invalid_requests:
            with pytest.raises(InvalidGenre):
                use_case.execute(request)

        mock_genre_repository.update.assert_not_called()

    def test_should_update_genre_with_valid_data(
        self,
        mock_genre_repository: IGenreRepository,
        mock_category_repository: ICategoryRepository,
    ) -> None:

        existing_categories = [
            Category(name="Terror", id=uuid.uuid4()),
            Category(name="Drama", id=uuid.uuid4()),
            Category(name="Comédia", id=uuid.uuid4()),
        ]
        selected_categories: Set[uuid.UUID] = {
            existing_categories[0].id,
            existing_categories[1].id,
        }

        genre_id = uuid.uuid4()
        existing_genre = Genre(
            id=genre_id,
            name="Old Name",
            is_active=False,
            categories={uuid.uuid4()},
        )

        mock_genre_repository.get_by_id.return_value = existing_genre
        mock_category_repository.list.return_value = existing_categories

        use_case = UpdateGenreUseCase(
            repository=mock_genre_repository,
            category_repository=mock_category_repository,
        )

        request = UpdateGenreRequest(
            id=genre_id,
            name="New Genre Name",
            is_active=True,
            categories=selected_categories,
        )

        use_case.execute(request)

        assert existing_genre.name == "New Genre Name"
        assert existing_genre.is_active is True
        assert existing_genre.categories == selected_categories
        mock_genre_repository.update.assert_called_once_with(existing_genre)
