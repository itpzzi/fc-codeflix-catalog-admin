import uuid
from unittest.mock import create_autospec

from src.core.category.application.usecases.list_category import (
    ListCategory,
)
from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)


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
        input = ListCategory.Input()
        use_case = ListCategory(repository=mock_repository)

        output = use_case.execute(input=input)

        assert output == ListCategory.Output(data=output.data)
        assert len(output.data) == 2
