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
class CreateGenreRequest:
    name: str
    is_active: bool = True
    categories: set[UUID] = field(default_factory=set)


@dataclass
class CreateGenreResponse:
    id: UUID


class CreateGenreUseCase:

    def __init__(
        self, repository: IGenreRepository, category_repository: ICategoryRepository
    ):
        self.repository = repository
        self.category_repository = category_repository

    def _pre_validated_categories(self, request: CreateGenreRequest):
        existent_categories_ids = {
            category.id for category in self.category_repository.list()
        }

        if not request.categories.issubset(existent_categories_ids):
            raise RelatedCategoriesNotFound(
                f"Categories with provided IDs not found: {request.categories - existent_categories_ids}"
            )

    def execute(self, request: CreateGenreRequest) -> CreateGenreResponse:
        self._pre_validated_categories(request)

        try:
            genre = Genre(
                name=request.name,
                categories=request.categories,
                is_active=request.is_active,
            )
        except ValueError as error:
            raise InvalidGenre(error)

        self.repository.save(genre)
        return CreateGenreResponse(id=genre.id)
