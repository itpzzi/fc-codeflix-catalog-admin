import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from src.core._shared.config import DEFAULT_PAGE_SIZE
from src.core.category.domain.category import Category
from src.core.genre.domain.genre import Genre
from src.django_project.category_app.repository import DjangoORMCategoryRepository
from src.django_project.genre_app.repository import DjangoORMGenreRepository


@pytest.fixture
def categories():
    return {
        "movie": Category(name="Filme", description="Longas divertidos"),
        "series": Category(name="Séries", description="Curtas divertidas"),
        "shows": Category(
            name="Shows", description="As melhores apresentações ao vivo"
        ),
        "documentary": Category(
            name="Documentários", description="Para o despertar da curiosidade"
        ),
    }


@pytest.fixture
def category_repository():
    return DjangoORMCategoryRepository()


@pytest.fixture
def genres(categories):
    return {
        "drama": Genre(
            name="Drama", categories={categories["movie"].id, categories["series"].id}
        ),
        "romance": Genre(name="Romance", categories=set()),
        "action": Genre(
            name="Ação", categories={categories["movie"].id, categories["series"].id}
        ),
        "thriller": Genre(
            name="Terror", categories={categories["movie"].id, categories["series"].id}
        ),
    }


@pytest.fixture
def genre_repository():
    return DjangoORMGenreRepository()


@pytest.mark.django_db
class TestGenreAPI:
    def setup_test_data(
        self,
        category_repository,
        categories,
        genre_repository,
        genres,
        selected_genres=None,
    ):
        """Helper to setup test data"""
        for category in categories.values():
            category_repository.save(category)

        for genre_name, genre in genres.items():
            if selected_genres is None or genre_name in selected_genres:
                genre_repository.save(genre)

    def test_list_genres_and_categories(
        self, categories, category_repository, genres, genre_repository
    ):
        self.setup_test_data(
            category_repository,
            {"movie": categories["movie"], "series": categories["series"]},
            genre_repository,
            {"drama": genres["drama"], "romance": genres["romance"]},
        )

        url = "/api/genres/"
        response = APIClient().get(url)
        categories_ids = [
            str(category_id) for category_id in genres["drama"].categories
        ]

        expected_data = {
            "data": [
                {
                    "id": str(genres["drama"].id),
                    "name": genres["drama"].name,
                    "categories": categories_ids,
                    "is_active": genres["drama"].is_active,
                },
                {
                    "id": str(genres["romance"].id),
                    "name": genres["romance"].name,
                    "categories": list(genres["romance"].categories),  # []
                    "is_active": genres["romance"].is_active,
                },
            ],
            "meta": {
                "total": 2,
                "current_page": 1,
                "per_page": DEFAULT_PAGE_SIZE,
            },
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data

    @pytest.mark.parametrize(
        "order_by,reverse,current_page,per_page,expected_genres",
        [
            ("name", False, 1, 2, ["Ação", "Drama"]),
            ("name", False, 2, 2, ["Romance", "Terror"]),
            ("name", True, 1, 2, ["Terror", "Romance"]),
            ("name", True, 2, 2, ["Drama", "Ação"]),
        ],
    )
    def test_list_genres_ordered_and_paginated_variations(
        self,
        order_by,
        reverse,
        current_page,
        per_page,
        expected_genres,
        categories,
        category_repository,
        genres,
        genre_repository,
    ):
        self.setup_test_data(category_repository, categories, genre_repository, genres)

        url = f"/api/genres/?order_by={order_by}&reverse={reverse}&current_page={current_page}&per_page={per_page}"
        response = APIClient().get(url)

        returned_genre_names = [genre["name"] for genre in response.data["data"]]

        assert response.status_code == status.HTTP_200_OK
        assert returned_genre_names == expected_genres

    def test_create_genre_with_invalid_name(self):
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

    def test_create_genre_with_valid_payload(
        self,
        categories,
        category_repository,
        genres,
        genre_repository,
    ):
        self.setup_test_data(
            category_repository,
            {"movie": categories["movie"], "series": categories["series"]},
            genre_repository,
            {},
        )

        url = "/api/genres/"
        data = {
            "name": genres["drama"].name,
            "is_active": genres["drama"].is_active,
            "categories": list(genres["drama"].categories),
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
        assert created_item.name == genres["drama"].name
        assert created_item.categories == genres["drama"].categories
        assert created_item.is_active == genres["drama"].is_active

    def test_delete_genre_with_invalid_id(self):
        url = "/api/genres/invalid_id/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"id": ["Must be a valid UUID."]}

    def test_delete_nonexistent_genre(self):
        url = f"/api/categories/{uuid.uuid4()}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_genre_success(
        self,
        categories,
        category_repository,
        genres,
        genre_repository,
    ):
        self.setup_test_data(
            category_repository,
            {"movie": categories["movie"], "series": categories["series"]},
            genre_repository,
            {"drama": genres["drama"], "romance": genres["romance"]},
        )

        url = f"/api/genres/{genres['drama'].id}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        deleted_genre = genre_repository.get_by_id(genres["drama"].id)
        assert deleted_genre is None

        persisted_genre = genre_repository.get_by_id(genres["romance"].id)
        assert persisted_genre is not None

    def test_update_genre_with_invalid_data(self):
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

    def test_update_genre_with_valid_data(
        self,
        categories,
        category_repository,
        genres,
        genre_repository,
    ):
        self.setup_test_data(
            category_repository,
            {"movie": categories["movie"], "series": categories["series"]},
            genre_repository,
            {"drama": genres["drama"], "romance": genres["romance"]},
        )

        url = f"/api/genres/{genres['drama'].id}/"
        data = {
            "name": "Drama Deactivation",
            "is_active": False,
            "categories": [],
        }

        response = APIClient().put(url, data, format="json")

        assert response is not None
        assert response.status_code == status.HTTP_204_NO_CONTENT

        updated_genre = genre_repository.get_by_id(genres["drama"].id)
        genre_items = genre_repository.list()

        assert len(genre_items) == 2
        assert updated_genre is not None
        assert updated_genre.name == "Drama Deactivation"
        assert not updated_genre.is_active
        assert updated_genre.categories == set()

    def test_update_nonexistent_genre(
        self,
        genres,
        genre_repository,
    ):
        genre_repository.save(genres["romance"])

        url = f"/api/genres/{genres['drama'].id}/"
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

    def test_update_genre_with_nonexistent_categories(
        self,
        genres,
        genre_repository,
    ):
        categories_fake = [str(uuid.uuid4()), str(uuid.uuid4())]
        genre_repository.save(genres["romance"])

        url = f"/api/genres/{genres['romance'].id}/"
        data = {
            "name": "Drama Deactivation",
            "is_active": False,
            "categories": categories_fake,
        }

        response = APIClient().put(url, data, format="json")

        assert response is not None
        assert response.status_code == status.HTTP_400_BAD_REQUEST
