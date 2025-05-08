import uuid
import pytest
from rest_framework.test import APIClient
from rest_framework import status

from operator import itemgetter
from src.django_project.category_app.repository import DjangoORMCategoryRepository
from src.core.category.domain.category import Category


@pytest.fixture
def category_movie() -> Category:
    return Category(name="Filme", description="Longas divertidos")


@pytest.fixture
def category_series() -> Category:
    return Category(name="Séries", description="Curtas divertidas")


@pytest.fixture
def category_repository() -> DjangoORMCategoryRepository:
    return DjangoORMCategoryRepository()


@pytest.mark.django_db
class TestCategoryAPI:

    def test_list_categories(
        self,
        category_movie: Category,
        category_series: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)
        category_repository.save(category_series)

        url = "/api/categories/"
        response = APIClient().get(url)

        expected_data = {
            "data": [
                {
                    "id": str(category_movie.id),
                    "name": category_movie.name,
                    "description": category_movie.description,
                    "is_active": category_movie.is_active,
                },
                {
                    "id": str(category_series.id),
                    "name": category_series.name,
                    "description": category_series.description,
                    "is_active": category_series.is_active,
                },
            ]
        }

        assert response.status_code == status.HTTP_200_OK
        assert response.data == expected_data


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
            "data": {
                "id": str(category_movie.id),
                "name": category_movie.name,
                "description": category_movie.description,
                "is_active": category_movie.is_active,
            }
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


@pytest.mark.django_db
class TestCreateAPI:
    def test_when_payload_is_invalid_return_400(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ):
        url = f"/api/categories/"
        data = {
            "name": "",
            "description": category_movie.description,
        }
        response = APIClient().post(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data
        assert "This field may not be blank." in response.data.get("name")

    def test_when_payload_is_valid_then_create_category_and_return_201(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ):
        url = f"/api/categories/"
        data = {
            "name": category_movie.name,
            "description": category_movie.description,
            "is_active": category_movie.is_active,
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
        assert created_item.name == category_movie.name
        assert created_item.description == category_movie.description
        assert created_item.is_active == category_movie.is_active


@pytest.mark.django_db
class TestUpdateAPI:
    def test_when_request_data_is_invalid_then_return_400(self):
        url = f"/api/categories/123123123/"
        data = {"name": ""}
        response = APIClient().put(url, data, format="json")
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {
            "id": ["Must be a valid UUID."],
            "description": ["This field is required."],
            "is_active": ["This field is required."],
            "name": ["This field may not be blank."],
        }

    def test_when_request_data_is_valid_then_update_category(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)

        url = f"/api/categories/{category_movie.id}/"
        data = {
            "name": "Filme Atualizado",
            "description": "Longas divertidos atualizados",
            "is_active": False,
        }
        response = APIClient().put(url, data, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        updated_category = category_repository.get_by_id(category_movie.id)
        assert updated_category is not None
        assert updated_category.name == "Filme Atualizado"
        assert updated_category.description == "Longas divertidos atualizados"
        assert updated_category.is_active is False

    def test_when_category_with_id_does_not_exist_then_return_404(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)

        url = f"/api/categories/{uuid.uuid4()}/"
        data = {
            "name": "Filme Atualizado",
            "description": "Longas divertidos atualizados",
            "is_active": False,
        }
        response = APIClient().put(url, data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestDeleteAPI:
    def test_when_category_pk_is_invalid_then_return_400(self) -> None:
        url = f"/api/categories/invalid_id/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data == {"id": ["Must be a valid UUID."]}

    def test_when_category_not_found_then_return_404(self) -> None:
        url = f"/api/categories/{uuid.uuid4()}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_when_category_found_then_delete_category(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)

        url = f"/api/categories/{category_movie.id}/"
        response = APIClient().delete(url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        deleted_category = category_repository.get_by_id(category_movie.id)
        assert deleted_category is None


@pytest.mark.django_db
class TestPartialUpdateAPI:
    def test_when_category_with_id_does_not_exist_then_return_404(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)

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
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
        payload,
        expected_changes,
    ) -> None:
        category_repository.save(category_movie)
        url = f"/api/categories/{category_movie.id}/"
        response = APIClient().patch(url, payload, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        updated = category_repository.get_by_id(category_movie.id)

        assert updated.id == category_movie.id
        assert expected_changes(updated)
        # Verifica que os campos não enviados se mantêm
        for field in {"name", "description", "is_active"} - payload.keys():
            assert getattr(updated, field) == getattr(category_movie, field)

    def test_partial_update_multiple_fields(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)

        url = f"/api/categories/{category_movie.id}/"
        payload = {
            "name": "Atualizado",
            "is_active": False,
        }
        response = APIClient().patch(url, payload, format="json")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        updated = category_repository.get_by_id(category_movie.id)

        assert updated.name == "Atualizado"
        assert updated.is_active is False
        assert updated.description == category_movie.description

    def test_partial_update_with_empty_payload_returns_400(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
    ) -> None:
        category_repository.save(category_movie)

        url = f"/api/categories/{category_movie.id}/"
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
    def test_partial_update_invalid_single_field_returns_400(
        self,
        category_movie: Category,
        category_repository: DjangoORMCategoryRepository,
        payload,
        expected_field,
    ) -> None:
        category_repository.save(category_movie)

        url = f"/api/categories/{category_movie.id}/"
        response = APIClient().patch(url, payload, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert expected_field in response.data
