from dataclasses import dataclass
from uuid import UUID

from src.core.category.domain.category_repository import (
    ICategoryRepository,
)


@dataclass
class ListCategoryItem:
    name: str
    description: str
    is_active: bool
    id: UUID


class ListCategory:

    @dataclass
    class Input:
        pass

    @dataclass
    class Output:
        data: list[ListCategoryItem]

    def __init__(self, repository: ICategoryRepository):
        self.repository = repository

    def execute(self, input: Input) -> Output:
        categories = self.repository.list()

        return ListCategory.Output(
            data=[
                ListCategoryItem(
                    name=category.name,
                    description=category.description,
                    is_active=category.is_active,
                    id=category.id,
                )
                for category in categories
            ]
        )
