from dataclasses import dataclass, field
from uuid import UUID

from src.core.category.domain.category_repository import ICategoryRepository
from src.core.genre.domain.genre_repository import (
    IGenreRepository,
)
from src.core.genre.application.exceptions import (
    GenreNotFound,
    InvalidGenre,
    RelatedCategoriesNotFound,
)
from src.core.genre.domain.genre import Genre


@dataclass
class UpdateGenreInput:
    id: UUID
    name: str
    categories: set[UUID]
    is_active: bool


@dataclass
class UpdateGenreOutput:
    pass


class UpdateGenreUseCase:

    def __init__(
        self, repository: IGenreRepository, category_repository: ICategoryRepository
    ):
        self.repository = repository
        self.category_repository = category_repository

    def _validate_genre_exists(self, request: UpdateGenreInput) -> Genre:
        genre_from_repo = self.repository.get_by_id(request.id)

        if not genre_from_repo:
            raise GenreNotFound(
                f"Cannot update non-existent genre. {request.id} not found"
            )

        return genre_from_repo

    def _validate_categories_exists(self, request: UpdateGenreInput):
        existent_categories_ids = {
            category.id for category in self.category_repository.list()
        }

        if not request.categories.issubset(existent_categories_ids):
            raise RelatedCategoriesNotFound(
                f"Categories with provided IDs not found: {request.categories - existent_categories_ids}"
            )

    def _update_genre_with_requested_data(
        self, genre_to_update: Genre, request: UpdateGenreInput
    ) -> Genre:
        try:
            genre_to_update.change_name(request.name)
            genre_to_update.categories = request.categories

            if not isinstance(request.is_active, bool):
                raise ValueError("is_active must be a boolean")

            if request.is_active:
                genre_to_update.activate()
            else:
                genre_to_update.deactivate()

            return genre_to_update

        except ValueError as error:
            raise InvalidGenre(error)

    def execute(self, request: UpdateGenreInput) -> None:
        genre_from_repo = self._validate_genre_exists(request)
        self._validate_categories_exists(request)
        genre_updated = self._update_genre_with_requested_data(
            genre_to_update=genre_from_repo, request=request
        )

        self.repository.update(genre_updated)
