from typing import List
from uuid import UUID

from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)


class InMemoryCategoryRepository(ICategoryRepository):
    def __init__(self, categories=None):
        self.categories = categories or []

    def save(self, category: Category) -> None:
        self.categories.append(category)

    def get_by_id(self, id: UUID) -> Category | None:
        for category in self.categories:
            if category.id == id:
                return category
        return None

    def delete(self, id: UUID) -> None:
        category_to_delete = self.get_by_id(id)
        self.categories.remove(category_to_delete)

    def update(self, category: Category) -> None:
        old_category = self.get_by_id(category.id)
        if old_category:
            self.categories.remove(old_category)
            self.categories.append(category)

    def list(self) -> List[Category]:
        return self.categories.copy()
