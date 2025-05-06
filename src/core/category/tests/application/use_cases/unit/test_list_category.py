from unittest.mock import create_autospec
import uuid

from src.core.category.application.usecases.list_category import (
    ListCategoryResponse,
    ListCategoryUseCase,
)
from src.core.category.application.category_repository import (
    CategoryRepositoryInterface,
)
from src.core.category.domain.category import Category


class TestListCategory:
    def test_list_all_the_categories(self):
        mock_category1 = Category(
            id=uuid.uuid4(),
            name="Filme",
            description="Categoria para filmes",
            is_active=True,
        )
        mock_category2 = Category(
            id=uuid.uuid4(),
            name="Série",
            description="Categoria para sequências",
            is_active=False,
        )
        mock_repository = create_autospec(CategoryRepositoryInterface)
        mock_repository.list.return_value = [mock_category1, mock_category2]
        use_case = ListCategoryUseCase(repository=mock_repository)

        response = use_case.execute()

        assert response == ListCategoryResponse(categories=response.categories)
        assert len(response.categories) == 2
