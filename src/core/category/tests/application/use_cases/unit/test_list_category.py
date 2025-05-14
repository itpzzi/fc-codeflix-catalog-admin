from unittest.mock import create_autospec

import pytest

from src.core._shared.config import DEFAULT_PAGE_SIZE
from src.core.category.application.usecases.list_category import (
    ListCategory,
    ListCategoryItem,
)
from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import ICategoryRepository


@pytest.fixture
def mock_category_list():
    return [
        Category(name="Filme", description="Longa-metragens de ficção", is_active=True),
        Category(name="Série", description="Episódios em temporadas", is_active=True),
        Category(
            name="Documentário", description="Conteúdos informativos", is_active=False
        ),
        Category(
            name="Show", description="Apresentações musicais ao vivo", is_active=True
        ),
    ]


@pytest.fixture
def mock_repository(mock_category_list):
    repo = create_autospec(ICategoryRepository)
    repo.list.return_value = mock_category_list
    return repo


class TestListCategory:
    def test_list_all_the_categories(self, mock_repository, mock_category_list):
        input = ListCategory.Input(per_page=4)
        use_case = ListCategory(repository=mock_repository)

        expected_data = [
            ListCategoryItem(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                is_active=cat.is_active,
            )
            for cat in mock_category_list
        ]

        output = use_case.execute(input=input)

        assert output.data == sorted(expected_data, key=lambda x: x.name)
        assert output.meta.total == 4
        assert output.meta.current_page == 1
        assert output.meta.per_page == 4

    def test_empty_repository(self):
        mock_repo = create_autospec(ICategoryRepository)
        mock_repo.list.return_value = []
        input = ListCategory.Input()
        use_case = ListCategory(repository=mock_repo)

        output = use_case.execute(input=input)

        assert output.data == []
        assert output.meta.total == 0
        assert output.meta.current_page == 1
        assert output.meta.per_page == 2

    @pytest.mark.parametrize(
        "order_by, reverse, current_page, per_page, expected_names",
        [
            ("name", False, 1, DEFAULT_PAGE_SIZE, ["Documentário", "Filme"]),
            ("name", False, 2, DEFAULT_PAGE_SIZE, ["Show", "Série"]),
            ("name", True, 1, DEFAULT_PAGE_SIZE, ["Série", "Show"]),
            ("name", True, 2, DEFAULT_PAGE_SIZE, ["Filme", "Documentário"]),
            ("description", False, 1, 4, ["Show", "Documentário", "Série", "Filme"]),
        ],
    )
    def test_ordering_and_pagination(
        self,
        mock_repository,
        mock_category_list,
        order_by,
        reverse,
        current_page,
        per_page,
        expected_names,
    ):
        input = ListCategory.Input(
            order_by=order_by,
            reverse=reverse,
            current_page=current_page,
            per_page=per_page,
        )
        use_case = ListCategory(repository=mock_repository)

        sorted_data = sorted(
            mock_category_list,
            key=lambda x: getattr(x, order_by),
            reverse=reverse,
        )
        paged_data = sorted_data[
            (current_page - 1) * per_page : current_page * per_page
        ]
        expected_data = [
            ListCategoryItem(
                id=cat.id,
                name=cat.name,
                description=cat.description,
                is_active=cat.is_active,
            )
            for cat in paged_data
        ]

        output = use_case.execute(input=input)

        assert [c.name for c in output.data] == expected_names
        assert output.data == expected_data
        assert output.meta.total == len(mock_category_list)
        assert output.meta.current_page == current_page
        assert output.meta.per_page == per_page
