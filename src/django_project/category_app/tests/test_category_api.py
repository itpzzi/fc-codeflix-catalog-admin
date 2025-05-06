import uuid
import pytest
from rest_framework.test import APIClient
from rest_framework import status

from operator import itemgetter
from django_project.category_app.repository import DjangoORMCategoryRepository
from src.core.category.domain.category import Category


@pytest.fixture
def category_movie() -> Category:
    return Category(name="Filme", description="Longas divertidos")


@pytest.fixture
def category_series() -> Category:
    return Category(name="Séries", description="Curtas divertidas")


@pytest.fixture
def category_documentary() -> Category:
    return Category(name="Documentários", description="Curtas informativas")


@pytest.fixture
def category_repository() -> DjangoORMCategoryRepository:
    return DjangoORMCategoryRepository()


@pytest.mark.django_db
class TestCategoryAPI:

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

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 3
        assert sorted(response.data, key=itemgetter("name")) == sorted(
            expected_data, key=itemgetter("name")
        )


@pytest.mark.django_db
class TestRetrieveAPI:

    def test_when_id_is_invalid_return_400(self) -> None:
        url = f"/api/categories/invalid_id/"
        response = APIClient().get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_return_category_when_exists(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)

        url = f"/api/categories/{category_movie.id}/"
        response = APIClient().get(url)

        expected_data = {
            "id": str(category_movie.id),
            "name": category_movie.name,
            "description": category_movie.description,
            "is_active": category_movie.is_active,
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data

    def test_return_404_when_category_does_not_exist(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)

        url = f"/api/categories/{uuid.uuid4()}/"
        response = APIClient().get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND
