from unittest.mock import create_autospec
import uuid

import pytest

from src.core.category.domain.category_repository import (
    ICategoryRepository,
)
from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.domain.category import Category

from src.core.category.application.usecases.get_category import (
    GetCategoryInput,
    GetCategoryOutput,
    GetCategoryUseCase,
)


class TestGetCategory:
    def test_when_category_exists_then_return_output_dto(self):
        mock_category = Category(
            id=uuid.uuid4(),
            name="Filme",
            description="Categoria para filmes",
            is_active=True,
        )
        mock_repository = create_autospec(ICategoryRepository)
        mock_repository.get_by_id.return_value = mock_category

        use_case = GetCategoryUseCase(repository=mock_repository)
        input = GetCategoryInput(id=mock_category.id)

        output = use_case.execute(input=input)

        assert output == GetCategoryOutput(
            id=mock_category.id,
            name="Filme",
            description="Categoria para filmes",
            is_active=True,
        )

    def test_when_category_not_found_then_raise_exception(self):
        mock_repository = create_autospec(ICategoryRepository)
        mock_repository.get_by_id.return_value = None

        use_case = GetCategoryUseCase(repository=mock_repository)
        input = GetCategoryInput(id=uuid.uuid4())

        with pytest.raises(CategoryNotFound):
            use_case.execute(input=input)
