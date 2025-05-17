from dataclasses import dataclass
from uuid import UUID

from src.core._shared.application.list_entity import ListEntityInput, ListEntityOutput
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
    Input = ListEntityInput
    Output = ListEntityOutput[ListCategoryItem]

    def __init__(self, repository: ICategoryRepository):
        self.repository = repository

    def execute(self, input: Input) -> Output:
        categories = self.repository.list()
        category_items = [
            ListCategoryItem(
                name=c.name, description=c.description, is_active=c.is_active, id=c.id
            )
            for c in categories
        ]
        return self.Output(input, category_items)
