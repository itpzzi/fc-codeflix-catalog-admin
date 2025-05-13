import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from src.core.category.domain.category import Category
from src.core.genre.domain.genre import Genre
from src.django_project.category_app.repository import DjangoORMCategoryRepository
from src.django_project.genre_app.repository import DjangoORMGenreRepository


@pytest.fixture
def category_movie() -> Category:
    return Category(name="Filme", description="Longas divertidos")


@pytest.fixture
def category_series() -> Category:
    return Category(name="Séries", description="Curtas divertidas")


@pytest.fixture
def category_repository() -> DjangoORMCategoryRepository:
    return DjangoORMCategoryRepository()


@pytest.fixture
def genre_drama(category_movie, category_series) -> Genre:
    return Genre(name="Drama", categories={category_movie.id, category_series.id})


@pytest.fixture
def genre_romance() -> Genre:
    return Genre(name="Romance", categories=set())


@pytest.fixture
def genre_repository():
    return DjangoORMGenreRepository()


@pytest.mark.django_db
class TestListAPI:
    def test_list_genres_and_categories(
        self,
        category_movie,
        category_series,
        category_repository,
        genre_drama,
        genre_romance,
        genre_repository,
    ):
        category_repository.save(category_movie)
        category_repository.save(category_series)

        genre_repository.save(genre_drama)
        genre_repository.save(genre_romance)

        url = "/api/genres/"
        response = APIClient().get(url)
        categories_ids = [str(category_id) for category_id in genre_drama.categories]

        expected_data = {
            "data": [
                {
                    "id": str(genre_drama.id),
                    "name": genre_drama.name,
                    "categories": categories_ids,
                    "is_active": genre_drama.is_active,
                },
                {
                    "id": str(genre_romance.id),
                    "name": genre_romance.name,
                    "categories": list(genre_romance.categories),  # []
                    "is_active": genre_romance.is_active,
                },
            ]
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data


@pytest.mark.django_db
class TestCreateAPI:
    def test_when_name_is_blank_return_400(self):
        url = "/api/genres/"
        data = {
            "name": "",  # inválido para serializer
            "is_active": True,
            "categories": [],
        }
        response = APIClient().post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
        assert "This field may not be blank." in response.data["name"]

    def test_when_payload_is_valid_then_create_category_and_return_201(
        self,
        category_repository,
        category_movie,
        category_series,
        genre_drama,
        genre_repository,
    ):
        category_repository.save(category_movie)
        category_repository.save(category_series)

        url = "/api/genres/"
        data = {
            "name": genre_drama.name,
            "is_active": genre_drama.is_active,
            "categories": list(genre_drama.categories),
        }

        response = APIClient().post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "id" in response.data

        id_str = response.data.get("id")
        assert isinstance(id_str, str)

        try:
            created_id = uuid.UUID(id_str, version=4)
        except ValueError:
            assert False, "ID retornado não é um UUID v4 válido"

        created_item = genre_repository.get_by_id(created_id)
        assert created_item is not None
        assert created_item.name == genre_drama.name
        assert created_item.categories == genre_drama.categories
        assert created_item.is_active == genre_drama.is_active


@pytest.mark.django_db
class TestDeleteAPI:
    def test_when_category_pk_is_invalid_then_return_400(self) -> None:
        url = "/api/genres/invalid_id/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"id": ["Must be a valid UUID."]}

    def test_when_category_not_found_then_return_404(self) -> None:
        url = f"/api/categories/{uuid.uuid4()}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_genre_success_with_related_categories(
        self,
        category_movie,
        category_series,
        category_repository,
        genre_drama,
        genre_romance,
        genre_repository,
    ) -> None:
        category_repository.save(category_movie)
        category_repository.save(category_series)

        genre_repository.save(genre_drama)
        genre_repository.save(genre_romance)

        url = f"/api/genres/{genre_drama.id}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        deleted_genre = genre_repository.get_by_id(genre_drama.id)
        assert deleted_genre is None

        persisted_genre = genre_repository.get_by_id(genre_romance.id)
        assert persisted_genre is not None


@pytest.mark.django_db
class TestUpdateAPI:

    def test_when_request_data_is_invalid_then_return_400(self):
        url = "/api/genres/123123123/"
        data = {
            "name": "",
            "is_active": True,
            "categories": [],
        }
        response = APIClient().put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
        assert "This field may not be blank." in response.data["name"]

    def test_when_request_data_is_valid_then_update_genre(
        self,
        category_movie,
        category_series,
        category_repository,
        genre_drama,
        genre_romance,
        genre_repository,
    ):
        category_repository.save(category_movie)
        category_repository.save(category_series)

        genre_repository.save(genre_drama)
        genre_repository.save(genre_romance)

        url = f"/api/genres/{genre_drama.id}/"
        data = {
            "name": "Drama Deactivation",
            "is_active": False,
            "categories": [],
        }

        response = APIClient().put(url, data, format="json")

        assert response is not None
        assert response.status_code == status.HTTP_204_NO_CONTENT

        updated_genre = genre_repository.get_by_id(genre_drama.id)
        genre_items = genre_repository.list()

        assert len(genre_items) == 2
        assert updated_genre is not None
        assert updated_genre.name == "Drama Deactivation"
        assert not updated_genre.is_active
        assert updated_genre.categories == set()

    def test_when_genre_does_not_exist_then_return_404(
        self, genre_drama, genre_romance, genre_repository
    ):
        genre_repository.save(genre_romance)

        url = f"/api/genres/{genre_drama.id}/"
        data = {
            "name": "Drama Deactivation",
            "is_active": False,
            "categories": [],
        }

        response = APIClient().put(url, data, format="json")
        genre_items = genre_repository.list()

        assert response is not None
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert len(genre_items) == 1

    def test_when_related_categories_do_not_exist_then_return_400(
        self, genre_romance, genre_repository
    ):
        categories_fake = [str(uuid.uuid4()), str(uuid.uuid4())]
        genre_repository.save(genre_romance)

        url = f"/api/genres/{genre_romance.id}/"
        data = {
            "name": "Drama Deactivation",
            "is_active": False,
            "categories": categories_fake,
        }

        response = APIClient().put(url, data, format="json")

        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
