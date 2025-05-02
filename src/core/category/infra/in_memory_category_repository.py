from src.core.category.application.category_repository import (
    CategoryRepositoryInterface,
)


class InMemoryCategoryRepository(CategoryRepositoryInterface):
    def __init__(self, categories=None):
        self.categories = categories or []

    def save(self, category):
        self.categories.append(category)
