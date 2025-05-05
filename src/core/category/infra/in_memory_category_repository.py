from uuid import UUID
from src.core.category.domain.category import Category
from src.core.category.application.category_repository import (
    CategoryRepositoryInterface,
)


class InMemoryCategoryRepository(CategoryRepositoryInterface):
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
