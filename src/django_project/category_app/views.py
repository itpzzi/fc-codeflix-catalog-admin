from uuid import UUID
from django.shortcuts import render
from rest_framework import viewsets

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND

from src.core.category.application.exceptions import CategoryNotFound
from django_project.category_app.repository import DjangoORMCategoryRepository

from src.core.category.application.usecases.list_category import (
    ListCategoryUseCase,
    ListCategoryRequest,
    ListCategoryResponse,
)

from src.core.category.application.usecases.get_category import (
    GetCategoryUseCase,
    GetCategoryRequest,
    GetCategoryResponse,
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

    def retrieve(self, request: Request, pk: None) -> Response:
        try:
            category_pk = UUID(pk)
        except ValueError:
            return Response(status=HTTP_400_BAD_REQUEST)

        input = GetCategoryRequest(id=category_pk)
        use_case = GetCategoryUseCase(repository=DjangoORMCategoryRepository())

        try:
            output = use_case.execute(request=input)
        except CategoryNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        category_output = {
            "id": str(output.id),
            "name": output.name,
            "description": output.description,
            "is_active": output.is_active,
        }

        return Response(
            status=HTTP_200_OK,
            data=category_output,
        )
