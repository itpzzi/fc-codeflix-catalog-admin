import uuid

import pytest

from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.domain.category import Category
from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)
from src.core.category.application.usecases.get_category import (
    GetCategoryRequest,
    GetCategoryResponse,
    GetCategoryUseCase,
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

        use_case = GetCategoryUseCase(repository=repository)
        request = GetCategoryRequest(id=category_movie.id)
        response = use_case.execute(request=request)

        assert response == GetCategoryResponse(
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

        use_case = GetCategoryUseCase(repository=repository)
        request = GetCategoryRequest(id=fake_id)
        with pytest.raises(
            CategoryNotFound, match=f"Category {fake_id} not found"
        ) as exc:
            use_case.execute(request=request)
