from unittest.mock import create_autospec
import uuid

import pytest
from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.application.usecases.delete_category import (
    DeleteCategoryInput,
    DeleteCategoryUseCase,
)
from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)


class TestDeleteCategory:
    def test_delete_category_from_repository(self):
        mock_category = Category(
            id=uuid.uuid4(),
            name="Filme",
            description="Categoria para filmes",
            is_active=True,
        )
        mock_repository = create_autospec(ICategoryRepository)
        mock_repository.get_by_id.return_value = mock_category

        use_case = DeleteCategoryUseCase(repository=mock_repository)
        request = DeleteCategoryInput(id=mock_category.id)

        use_case.execute(request)

        mock_repository.delete.assert_called_once_with = mock_category.id

    def test_when_category_not_found_then_raises_exception(self):
        mock_repository = create_autospec(ICategoryRepository)
        mock_repository.get_by_id.return_value = None

        use_case = DeleteCategoryUseCase(repository=mock_repository)
        request = DeleteCategoryInput(id=uuid.uuid4())

        with pytest.raises(
            CategoryNotFound,
            match=f"Cannot delete non-existent category. {request.id} not found",
        ):
            use_case.execute(request)

        mock_repository.delete.assert_not_called()
        assert mock_repository.delete.called is False
