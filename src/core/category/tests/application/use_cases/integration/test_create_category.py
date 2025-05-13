from unittest.mock import MagicMock
from uuid import UUID
import pytest

from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)
from src.core.category.application.exceptions import InvalidCategory
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)
from src.core.category.application.usecases.create_category import (
    CreateCategoryInput,
    CreateCategoryOutput,
    CreateCategory,
)


class TestCreateCategory:
    def test_create_category_with_valid_data(self):
        repository = InMemoryCategoryRepository()
        use_case = CreateCategory(repository=repository)
        input = CreateCategoryInput(
            name="Série", description="Muita ação", is_active=True
        )

        output = use_case.execute(input=input)

        assert output.id is not None
        assert isinstance(output.id, UUID)
        assert len(repository.categories) == 1

        persisted_category = repository.categories[0]
        assert persisted_category.name == "Série"
        assert persisted_category.description == "Muita ação"
        assert persisted_category.is_active is True
        assert persisted_category.id == output.id

    def test_create_inactive_category_with_valid_data(self):
        repository = InMemoryCategoryRepository()
        use_case = CreateCategory(repository=repository)
        input = CreateCategoryInput(
            name="Filme",
            description="Categoria para filmes",
            is_active=False,
        )

        output = use_case.execute(input=input)
        persisted_category = repository.categories[0]

        assert persisted_category.id == output.id
        assert persisted_category.name == "Filme"
        assert persisted_category.description == "Categoria para filmes"
        assert persisted_category.is_active == False
