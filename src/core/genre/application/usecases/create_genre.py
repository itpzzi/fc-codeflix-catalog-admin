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


class CreateGenre:

    @dataclass
    class Input:
        name: str
        is_active: bool = True
        categories: set[UUID] = field(default_factory=set)

    @dataclass
    class Output:
        id: UUID

    def __init__(
        self, repository: IGenreRepository, category_repository: ICategoryRepository
    ):
        self.repository = repository
        self.category_repository = category_repository

    def _validate_categories_exists(self, input: Input):
        existent_categories_ids = {
            category.id for category in self.category_repository.list()
        }

        if not input.categories.issubset(existent_categories_ids):
            raise RelatedCategoriesNotFound(
                f"Categories with provided IDs not found: {input.categories - existent_categories_ids}"
            )

    def execute(self, input: Input) -> Output:
        self._validate_categories_exists(input)

        try:
            genre = Genre(
                name=input.name,
                categories=input.categories,
                is_active=input.is_active,
            )
        except ValueError as error:
            raise InvalidGenre(error)

        self.repository.save(genre)
        return self.Output(id=genre.id)
