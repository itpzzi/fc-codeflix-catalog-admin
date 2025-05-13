import uuid

import pytest

from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.application.usecases.get_category import (
    GetCategory,
)
from src.core.category.domain.category import Category
from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)


class TestGetCategory:
    def test_get_category_by_id(self):
        category_movie = Category(
            name="Filme", description="Filmes em geral.", is_active=True
        )
        category_show = Category(
            name="Série", description="Muitos episódios para curtir.", is_active=True
        )
        repository = InMemoryCategoryRepository(
            categories=[category_movie, category_show]
        )

        use_case = GetCategory(repository=repository)
        input = GetCategory.Input(id=category_movie.id)
        output = use_case.execute(input=input)

        assert output == GetCategory.Output(
            id=category_movie.id,
            name="Filme",
            description="Filmes em geral.",
            is_active=True,
        )

    def test_get_category_by_id_with_invalid_id(self):
        category_movie = Category(
            name="Filme", description="Filmes em geral.", is_active=True
        )
        category_show = Category(
            name="Série", description="Muitos episódios para curtir.", is_active=True
        )
        repository = InMemoryCategoryRepository(
            categories=[category_movie, category_show]
        )
        fake_id = uuid.uuid4()

        use_case = GetCategory(repository=repository)
        input = GetCategory.Input(id=fake_id)
        with pytest.raises(
            CategoryNotFound, match=f"Category {fake_id} not found"
        ):
            use_case.execute(input=input)
