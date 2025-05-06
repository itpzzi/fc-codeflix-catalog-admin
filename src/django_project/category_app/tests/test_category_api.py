import pytest
from rest_framework.test import APIClient

from operator import itemgetter
from django_project.category_app.repository import DjangoORMCategoryRepository
from src.core.category.domain.category import Category


@pytest.mark.django_db
class TestCategoryAPI:

    @pytest.fixture
    def category_movie(self) -> Category:
        return Category(name="Filme", description="Longas divertidos")

    @pytest.fixture
    def category_series(self) -> Category:
        return Category(name="Séries", description="Curtas divertidas")

    @pytest.fixture
    def category_documentary(self) -> Category:
        return Category(name="Documentários", description="Curtas informativas")

    @pytest.fixture
    def category_repository(self) -> DjangoORMCategoryRepository:
        return DjangoORMCategoryRepository()

    def test_list_categories(
        self,
        category_movie: Category,
        category_series: Category,
        category_documentary: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)
        category_repository.save(category_series)
        category_repository.save(category_documentary)

        url = "/api/categories/"
        response = APIClient().get(url)

        expected_data = [
            {
                "id": str(category_movie.id),
                "name": category_movie.name,
                "description": category_movie.description,
                "is_active": category_movie.is_active,
            },
            {
                "id": str(category_documentary.id),
                "name": category_documentary.name,
                "description": category_documentary.description,
                "is_active": category_documentary.is_active,
            },
            {
                "id": str(category_series.id),
                "name": category_series.name,
                "description": category_series.description,
                "is_active": category_series.is_active,
            },
        ]

        assert response.status_code == 200
        assert len(response.data) == 3
        assert sorted(response.data, key=itemgetter("name")) == sorted(
            expected_data, key=itemgetter("name")
        )
