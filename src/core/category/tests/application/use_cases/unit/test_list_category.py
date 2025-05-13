from unittest.mock import create_autospec
import uuid

from src.core.category.application.usecases.list_category import (
    ListCategoryInput,
    ListCategoryOutput,
    ListCategoryUseCase,
)
from src.core.category.domain.category_repository import (
    ICategoryRepository,
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
        mock_repository = create_autospec(ICategoryRepository)
        mock_repository.list.return_value = [mock_category1, mock_category2]
        input = ListCategoryInput()
        use_case = ListCategoryUseCase(repository=mock_repository)

        output = use_case.execute(input=input)

        assert output == ListCategoryOutput(data=output.data)
        assert len(output.data) == 2
