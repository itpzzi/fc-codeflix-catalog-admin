from dataclasses import dataclass
from uuid import UUID
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)


@dataclass
class CategoryOutput:
    name: str
    description: str
    is_active: bool
    id: UUID


@dataclass
class ListCategoryInput:
    pass


@dataclass
class ListCategoryOutput:
    data: list[CategoryOutput]


class ListCategoryUseCase:

    def __init__(self, repository: ICategoryRepository):
        self.repository = repository

    def execute(self, request: ListCategoryInput) -> ListCategoryOutput:
        categories = self.repository.list()

        return ListCategoryOutput(
            data=[
                CategoryOutput(
                    name=category.name,
                    description=category.description,
                    is_active=category.is_active,
                    id=category.id,
                )
                for category in categories
            ]
        )
