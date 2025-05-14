import uuid

from src.core.category.application.usecases.list_category import (
    ListCategory,
    ListCategoryItem,
)
from src.core.category.domain.category import Category
from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
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
        repository = InMemoryCategoryRepository(categories=[])
        repository.save(mock_category1)
        repository.save(mock_category2)

        input = ListCategory.Input()
        use_case = ListCategory(repository=repository)

        output = use_case.execute(input=input)

        assert len(output.data) == 2
        assert (
            output.data
            == ListCategory.Output(
                input,
                data=[
                    ListCategoryItem(
                        id=mock_category1.id,
                        name=mock_category1.name,
                        description=mock_category1.description,
                        is_active=mock_category1.is_active,
                    ),
                    ListCategoryItem(
                        id=mock_category2.id,
                        name=mock_category2.name,
                        description=mock_category2.description,
                        is_active=mock_category2.is_active,
                    ),
                ],
            ).data
        )
        assert output.meta.total == 2
        assert output.meta.current_page == 1
        assert output.meta.per_page == 2

    def test_when_no_categories_then_return_empty_list(self):
        repository = InMemoryCategoryRepository(categories=[])
        use_case = ListCategory(repository=repository)
        input = ListCategory.Input()

        output = use_case.execute(input=input)

        assert len(output.data) == 0
        assert output.data == ListCategory.Output(input, data=[]).data
        assert output.meta.total == 0
        assert output.meta.current_page == 1
        assert output.meta.per_page == 2
