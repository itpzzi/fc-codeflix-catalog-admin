from dataclasses import dataclass
from uuid import UUID
from src.core.category.application.category_repository import (
    CategoryRepositoryInterface,
)


@dataclass
class CategoryOutput:
    name: str
    description: str
    is_active: bool
    id: UUID


@dataclass
class ListCategoryResponse:
    categories: list[CategoryOutput]


class ListCategoryUseCase:

    def __init__(self, repository: CategoryRepositoryInterface):
        self.repository = repository

    def execute(self) -> ListCategoryResponse:
        categories = self.repository.list()

        return ListCategoryResponse(
            categories=[
                CategoryOutput(
                    name=category.name,
                    description=category.description,
                    is_active=category.is_active,
                    id=category.id,
                )
                for category in categories
            ]
        )
