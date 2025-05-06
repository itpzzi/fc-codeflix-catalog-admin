from django.test import TestCase

from rest_framework.test import APITestCase


class TestCategoryAPI(APITestCase):
    def test_list_categories(self):
        url = "/api/categories/"
        response = self.client.get(url)

        expected_data = {
            "categories": [
                {
                    "id": 1,
                    "name": "Filme",
                    "description": "Longas divertidos",
                    "is_active": True,
                },
                {
                    "id": 2,
                    "name": "Séries",
                    "description": "Curtas divertidas",
                    "is_active": True,
                },
                {
                    "id": 3,
                    "name": "Documentários",
                    "description": "Curtas informativas",
                    "is_active": True,
                },
            ]
        }

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["categories"]), 3)
        self.assertEqual(response.data, expected_data)
