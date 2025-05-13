from dataclasses import dataclass, field
from uuid import UUID

from src.core.category.domain.category_repository import ICategoryRepository
from src.core.genre.domain.genre_repository import (
    IGenreRepository,
)
from src.core.genre.application.exceptions import (
    InvalidGenre,
    RelatedCategoriesNotFound,
)
from src.core.genre.domain.genre import Genre


@dataclass
class CreateGenreInput:
    name: str
    is_active: bool = True
    categories: set[UUID] = field(default_factory=set)


@dataclass
class CreateGenreOutput:
    id: UUID


class CreateGenreUseCase:

    def __init__(
        self, repository: IGenreRepository, category_repository: ICategoryRepository
    ):
        self.repository = repository
        self.category_repository = category_repository

    def _validate_categories_exists(self, request: CreateGenreInput):
        existent_categories_ids = {
            category.id for category in self.category_repository.list()
        }

        if not request.categories.issubset(existent_categories_ids):
            raise RelatedCategoriesNotFound(
                f"Categories with provided IDs not found: {request.categories - existent_categories_ids}"
            )

    def execute(self, request: CreateGenreInput) -> CreateGenreOutput:
        self._validate_categories_exists(request)

        try:
            genre = Genre(
                name=request.name,
                categories=request.categories,
                is_active=request.is_active,
            )
        except ValueError as error:
            raise InvalidGenre(error)

        self.repository.save(genre)
        return CreateGenreOutput(id=genre.id)
