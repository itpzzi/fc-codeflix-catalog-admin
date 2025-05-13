from unittest.mock import create_autospec
import uuid

import pytest
from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)
from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.application.usecases.delete_category import (
    DeleteCategoryInput,
    DeleteCategory,
)
from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)


class TestDeleteCategory:
    def test_delete_category_from_repository(self):
        category_movie = Category(
            name="Filme", description="Filmes em geral.", is_active=True
        )
        repository = InMemoryCategoryRepository(categories=[category_movie])
        use_case = DeleteCategory(repository=repository)
        input = DeleteCategoryInput(id=category_movie.id)

        assert repository.get_by_id(id=category_movie.id) is not None
        output = use_case.execute(input=input)

        assert repository.get_by_id(id=category_movie.id) is None
        assert output is None
