from django.test import TestCase
from rest_framework.test import APITestCase

from django_project.category_app.repository import DjangoORMCategoryRepository
from src.core.category.domain.category import Category


class TestCategoryAPI(APITestCase):
    def test_list_categories(self):

        category_movie = Category(name="Filme", description="Longas divertidos")
        category_series = Category(name="Séries", description="Curtas divertidas")
        category_documentary = Category(
            name="Documentários", description="Curtas informativas"
        )

        repository = DjangoORMCategoryRepository()
        repository.save(category_movie)
        repository.save(category_series)
        repository.save(category_documentary)

        url = "/api/categories/"
        response = self.client.get(url)

        expected_data = [
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
            {
                "id": str(category_documentary.id),
                "name": category_documentary.name,
                "description": category_documentary.description,
                "is_active": category_documentary.is_active,
            },
        ]

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 3)
        self.assertCountEqual(response.data, expected_data)
