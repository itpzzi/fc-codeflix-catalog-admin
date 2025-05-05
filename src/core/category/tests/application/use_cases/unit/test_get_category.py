from unittest.mock import create_autospec
import uuid

import pytest

from src.core.category.application.category_repository import (
    CategoryRepositoryInterface,
)
from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.domain.category import Category

from src.core.category.application.usecases.get_category import (
    GetCategoryRequest,
    GetCategoryResponse,
    GetCategoryUseCase,
)


class TestGetCategory:
    def test_when_category_exists_then_return_response_dto(self):
        mock_category = Category(
            id=uuid.uuid4(),
            name="Filme",
            description="Categoria para filmes",
            is_active=True,
        )
        mock_repository = create_autospec(CategoryRepositoryInterface)
        mock_repository.get_by_id.return_value = mock_category

        use_case = GetCategoryUseCase(repository=mock_repository)
        request = GetCategoryRequest(id=mock_category.id)

        response = use_case.execute(request)

        assert response == GetCategoryResponse(
            id=mock_category.id,
            name="Filme",
            description="Categoria para filmes",
            is_active=True,
        )

    def test_when_category_not_found_then_raise_exception(self):
        mock_repository = create_autospec(CategoryRepositoryInterface)
        mock_repository.get_by_id.return_value = None

        use_case = GetCategoryUseCase(repository=mock_repository)
        request = GetCategoryRequest(id=uuid.uuid4())

        with pytest.raises(CategoryNotFound):
            use_case.execute(request)
