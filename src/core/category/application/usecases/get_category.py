from dataclasses import asdict, dataclass
from uuid import UUID

from src.core.category.domain.category_repository import (
    ICategoryRepository,
)
from src.core.category.application.exceptions import InvalidCategory
from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.domain.category import Category


@dataclass
class GetCategoryInput:
    id: UUID


@dataclass
class GetCategoryOutput:
    id: UUID
    name: str
    description: str
    is_active: bool


class GetCategory:

    def __init__(self, repository: ICategoryRepository):
        self.repository = repository

    def execute(self, input: GetCategoryInput) -> GetCategoryOutput:
        category_from_repo = self.repository.get_by_id(input.id)
        if category_from_repo is None:
            raise CategoryNotFound(f"Category {input.id} not found")

        try:
            category = Category(
                id=category_from_repo.id,
                name=category_from_repo.name,
                description=category_from_repo.description,
                is_active=category_from_repo.is_active,
            )
        except ValueError as error:
            raise InvalidCategory(error)

        return GetCategoryOutput(
            id=category.id,
            name=category.name,
            description=category.description,
            is_active=category.is_active,
        )
