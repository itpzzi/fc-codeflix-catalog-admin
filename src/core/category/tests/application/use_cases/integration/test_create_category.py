from unittest.mock import MagicMock
from uuid import UUID
import pytest

from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)
from src.core.category.application.exceptions import InvalidCategory
from src.core.category.application.category_repository import (
    CategoryRepositoryInterface,
)
from src.core.category.application.usecases.create_category import (
    CreateCategoryRequest,
    CreateCategoryResponse,
    CreateCategoryUseCase,
)


class TestCreateCategory:
    def test_create_category_with_valid_data(self):
        repository = InMemoryCategoryRepository()
        use_case = CreateCategoryUseCase(repository=repository)
        request = CreateCategoryRequest(
            name="Série", description="Muita ação", is_active=True
        )

        response = use_case.execute(request=request)

        assert response.id is not None
        assert isinstance(response.id, UUID)
        assert len(repository.categories) == 1

        persisted_category = repository.categories[0]
        assert persisted_category.name == "Série"
        assert persisted_category.description == "Muita ação"
        assert persisted_category.is_active is True
        assert persisted_category.id == response.id

    def test_create_inactive_category_with_valid_data(self):
        repository = InMemoryCategoryRepository()
        use_case = CreateCategoryUseCase(repository=repository)
        request = CreateCategoryRequest(
            name="Filme",
            description="Categoria para filmes",
            is_active=False,
        )

        response = use_case.execute(request)
        persisted_category = repository.categories[0]

        assert persisted_category.id == response.id
        assert persisted_category.name == "Filme"
        assert persisted_category.description == "Categoria para filmes"
        assert persisted_category.is_active == False
