from uuid import UUID
from django.shortcuts import render
from rest_framework import viewsets

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_404_NOT_FOUND,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
)

from src.django_project.category_app.serializers import (
    CreateCategoryRequestSerializer,
    CreateCategoryResponseSerializer,
    DeleteCategoryRequestSerializer,
    ListCategoryResponseSerializer,
    RetrieveCategoryRequestSerializer,
    RetrieveCategoryResponseSerializer,
    UpdateCategoryRequestSerializer,
)
from src.core.category.application.exceptions import CategoryNotFound
from src.django_project.category_app.repository import DjangoORMCategoryRepository

from src.core.category.application.usecases.list_category import (
    ListCategoryUseCase,
    ListCategoryInput,
)

from src.core.category.application.usecases.get_category import (
    GetCategoryUseCase,
    GetCategoryInput,
)

from src.core.category.application.usecases.create_category import (
    CreateCategoryUseCase,
    CreateCategoryInput,
)
from src.core.category.application.usecases.update_category import (
    UpdateCategoryUseCase,
    UpdateCategoryInput,
)
from src.core.category.application.usecases.delete_category import (
    DeleteCategoryUseCase,
    DeleteCategoryInput,
)


class CategoryViewSet(viewsets.ViewSet):
    def list(self, request: Request) -> Response:
        input = ListCategoryInput()
        use_case = ListCategoryUseCase(repository=DjangoORMCategoryRepository())

        output = use_case.execute(input)

        serializer = ListCategoryResponseSerializer(instance=output)
        return Response(status=HTTP_200_OK, data=serializer.data)

    def retrieve(self, request: Request, pk: None) -> Response:
        deserializer = RetrieveCategoryRequestSerializer(data={"id": pk})
        deserializer.is_valid(raise_exception=True)

        input = GetCategoryInput(id=deserializer.data.get("id"))
        use_case = GetCategoryUseCase(repository=DjangoORMCategoryRepository())

        try:
            output = use_case.execute(input=input)
        except CategoryNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        serializer = RetrieveCategoryResponseSerializer(instance=output)
        return Response(
            status=HTTP_200_OK,
            data=serializer.data,
        )

    def create(self, request: Request) -> Response:
        deserializer = CreateCategoryRequestSerializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        input = CreateCategoryInput(**deserializer.validated_data)
        use_case = CreateCategoryUseCase(repository=DjangoORMCategoryRepository())

        output = use_case.execute(input=input)

        return Response(
            status=HTTP_201_CREATED,
            data=CreateCategoryResponseSerializer(instance=output).data,
        )

    def update(self, request: Request, pk: UUID = None):
        deserializer = UpdateCategoryRequestSerializer(
            data={
                **request.data,
                "id": pk,
            }
        )
        deserializer.is_valid(raise_exception=True)

        input = UpdateCategoryInput(**deserializer.validated_data)
        use_case = UpdateCategoryUseCase(repository=DjangoORMCategoryRepository())
        try:
            use_case.execute(input=input)
        except CategoryNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request: Request, pk: UUID = None):
        deserializer = DeleteCategoryRequestSerializer(data={"id": pk})
        deserializer.is_valid(raise_exception=True)

        input = DeleteCategoryInput(**deserializer.validated_data)
        use_case = DeleteCategoryUseCase(repository=DjangoORMCategoryRepository())
        try:
            use_case.execute(input)
        except CategoryNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk: UUID = None):
        deserializer = UpdateCategoryRequestSerializer(
            data={
                **request.data,
                "id": pk,
            },
            partial=True,
        )
        deserializer.is_valid(raise_exception=True)

        input = UpdateCategoryInput(**deserializer.validated_data)
        use_case = UpdateCategoryUseCase(repository=DjangoORMCategoryRepository())
        try:
            use_case.execute(input=input)
        except CategoryNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)
