import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

from src.core.category.domain.category import Category
from src.django_project.category_app.repository import DjangoORMCategoryRepository


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


@pytest.mark.django_db
class TestCategoryAPI:
    def setup_test_data(
        self, category_repository, categories, selected_categories=None
    ):
        """Helper to setup test data"""
        for category_name, category in categories.items():
            if selected_categories is None or category_name in selected_categories:
                category_repository.save(category)

    def test_list_categories(self, categories, category_repository):
        self.setup_test_data(
            category_repository,
            {"movie": categories["movie"], "series": categories["series"]},
        )

        url = "/api/categories/"
        response = APIClient().get(url)

        expected_data = {
            "data": [
                {
                    "id": str(categories["movie"].id),
                    "name": categories["movie"].name,
                    "description": categories["movie"].description,
                    "is_active": categories["movie"].is_active,
                },
                {
                    "id": str(categories["series"].id),
                    "name": categories["series"].name,
                    "description": categories["series"].description,
                    "is_active": categories["series"].is_active,
                },
            ]
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data

    @pytest.mark.parametrize(
        "order_by,reverse,current_page,per_page,expected_categories",
        [
            ("name", False, 1, 2, ["Documentários", "Filme"]),
            ("name", False, 2, 2, ["Shows", "Séries"]),
            ("name", True, 1, 2, ["Séries", "Shows"]),
            ("name", True, 2, 2, ["Filme", "Documentários"]),
        ],
    )
    def test_list_categories_ordered_and_paginated_variations(
        self,
        order_by,
        reverse,
        current_page,
        per_page,
        expected_categories,
        categories,
        category_repository,
    ):
        self.setup_test_data(category_repository, categories)

        url = f"/api/categories/?order_by={order_by}&reverse={reverse}&current_page={current_page}&per_page={per_page}"
        response = APIClient().get(url)

        returned_category_names = [
            category["name"] for category in response.data["data"]
        ]

        assert response.status_code == status.HTTP_200_OK
        assert returned_category_names == expected_categories

    def test_retrieve_category_with_invalid_id(self):
        url = "/api/categories/invalid_id/"
        response = APIClient().get(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_retrieve_existing_category(self, categories, category_repository):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{categories['movie'].id}/"
        response = APIClient().get(url)

        expected_data = {
            "data": {
                "id": str(categories["movie"].id),
                "name": categories["movie"].name,
                "description": categories["movie"].description,
                "is_active": categories["movie"].is_active,
            }
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data

    def test_retrieve_nonexistent_category(self, categories, category_repository):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{uuid.uuid4()}/"
        response = APIClient().get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_create_category_with_invalid_payload(self, categories):
        url = "/api/categories/"
        data = {
            "name": "",
            "description": categories["movie"].description,
        }
        response = APIClient().post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
        assert "This field may not be blank." in response.data.get("name")

    def test_create_category_with_valid_payload(self, categories, category_repository):
        url = "/api/categories/"
        data = {
            "name": categories["movie"].name,
            "description": categories["movie"].description,
            "is_active": categories["movie"].is_active,
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

        created_item = category_repository.get_by_id(created_id)
        assert created_item is not None
        assert created_item.name == categories["movie"].name
        assert created_item.description == categories["movie"].description
        assert created_item.is_active == categories["movie"].is_active

    def test_update_category_with_invalid_data(self):
        url = "/api/categories/123123123/"
        data = {"name": ""}
        response = APIClient().put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "id": ["Must be a valid UUID."],
            "description": ["This field is required."],
            "is_active": ["This field is required."],
            "name": ["This field may not be blank."],
        }

    def test_update_category_with_valid_data(self, categories, category_repository):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{categories['movie'].id}/"
        data = {
            "name": "Filme Atualizado",
            "description": "Longas divertidos atualizados",
            "is_active": False,
        }
        response = APIClient().put(url, data, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        updated_category = category_repository.get_by_id(categories["movie"].id)
        assert updated_category is not None
        assert updated_category.name == "Filme Atualizado"
        assert updated_category.description == "Longas divertidos atualizados"
        assert updated_category.is_active is False

    def test_update_nonexistent_category(self, categories, category_repository):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{uuid.uuid4()}/"
        data = {
            "name": "Filme Atualizado",
            "description": "Longas divertidos atualizados",
            "is_active": False,
        }
        response = APIClient().put(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_category_with_invalid_id(self):
        url = "/api/categories/invalid_id/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"id": ["Must be a valid UUID."]}

    def test_delete_nonexistent_category(self):
        url = f"/api/categories/{uuid.uuid4()}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_delete_existing_category(self, categories, category_repository):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{categories['movie'].id}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        deleted_category = category_repository.get_by_id(categories["movie"].id)
        assert deleted_category is None

    def test_partial_update_nonexistent_category(self, categories, category_repository):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{uuid.uuid4()}/"
        data = {
            "name": "Filme Atualizado",
            "description": "Longas divertidos atualizados",
            "is_active": False,
        }
        response = APIClient().patch(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.parametrize(
        "payload, expected_changes",
        [
            ({"name": "Movie"}, lambda c: (c.name == "Movie")),
            (
                {"description": "Funny long movies"},
                lambda c: (c.description == "Funny long movies"),
            ),
            ({"is_active": False}, lambda c: (c.is_active is False)),
        ],
    )
    def test_partial_update_single_field(
        self,
        categories,
        category_repository,
        payload,
        expected_changes,
    ):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{categories['movie'].id}/"
        response = APIClient().patch(url, payload, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        updated = category_repository.get_by_id(categories["movie"].id)

        assert updated.id == categories["movie"].id
        assert expected_changes(updated)
        # Verifica que os campos não enviados se mantêm
        for field in {"name", "description", "is_active"} - payload.keys():
            assert getattr(updated, field) == getattr(categories["movie"], field)

    def test_partial_update_multiple_fields(self, categories, category_repository):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{categories['movie'].id}/"
        payload = {
            "name": "Atualizado",
            "is_active": False,
        }
        response = APIClient().patch(url, payload, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        updated = category_repository.get_by_id(categories["movie"].id)

        assert updated.name == "Atualizado"
        assert updated.is_active is False
        assert updated.description == categories["movie"].description

    def test_partial_update_with_empty_payload(self, categories, category_repository):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{categories['movie'].id}/"
        response = APIClient().patch(url, {}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "non_field_errors" in response.data
        assert (
            "At least one field must be provided for partial update."
            in response.data["non_field_errors"]
        )

    @pytest.mark.parametrize(
        "payload, expected_field",
        [
            ({"name": ""}, "name"),
            ({"description": None}, "description"),
            ({"is_active": "not_a_bool"}, "is_active"),
        ],
    )
    def test_partial_update_invalid_field(
        self,
        categories,
        category_repository,
        payload,
        expected_field,
    ):
        self.setup_test_data(category_repository, {"movie": categories["movie"]})

        url = f"/api/categories/{categories['movie'].id}/"
        response = APIClient().patch(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert expected_field in response.data
