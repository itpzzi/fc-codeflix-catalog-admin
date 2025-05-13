from unittest.mock import create_autospec
import uuid

from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)
from src.core.category.application.usecases.list_category import (
    CategoryOutput,
    ListCategoryInput,
    ListCategoryOutput,
    ListCategory,
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
        repository = InMemoryCategoryRepository(categories=[])
        repository.save(mock_category1)
        repository.save(mock_category2)

        input = ListCategoryInput()
        use_case = ListCategory(repository=repository)

        output = use_case.execute(input=input)

        assert output == ListCategoryOutput(data=output.data)
        assert len(output.data) == 2
        assert output == ListCategoryOutput(
            data=[
                CategoryOutput(
                    id=mock_category1.id,
                    name=mock_category1.name,
                    description=mock_category1.description,
                    is_active=mock_category1.is_active,
                ),
                CategoryOutput(
                    id=mock_category2.id,
                    name=mock_category2.name,
                    description=mock_category2.description,
                    is_active=mock_category2.is_active,
                ),
            ]
        )

    def test_when_no_categories_then_return_empty_list(self):
        repository = InMemoryCategoryRepository(categories=[])
        use_case = ListCategory(repository=repository)
        input = ListCategoryInput()

        output = use_case.execute(input=input)

        assert len(output.data) == 0
        assert output == ListCategoryOutput(data=[])
