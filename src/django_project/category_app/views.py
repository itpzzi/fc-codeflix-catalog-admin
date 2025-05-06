from django.shortcuts import render
from rest_framework import viewsets

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK

from django_project.category_app.repository import DjangoORMCategoryRepository

from src.core.category.application.usecases.list_category import (
    ListCategoryUseCase,
    ListCategoryRequest,
    ListCategoryResponse,
)


class CategoryViewSet(viewsets.ViewSet):
    def list(self, request: Request) -> Response:
        input = ListCategoryRequest()
        use_case = ListCategoryUseCase(repository=DjangoORMCategoryRepository())

        output = use_case.execute(input)

        categories = [
            {
                "id": str(category.id),
                "name": category.name,
                "description": category.description,
                "is_active": category.is_active,
            }
            for category in output.data
        ]

        return Response(status=HTTP_200_OK, data=categories)
