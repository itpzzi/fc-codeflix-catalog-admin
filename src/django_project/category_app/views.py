from uuid import UUID

from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_404_NOT_FOUND,
)

from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.application.usecases.create_category import (
    CreateCategory,
)
from src.core.category.application.usecases.delete_category import (
    DeleteCategory,
)
from src.core.category.application.usecases.get_category import (
    GetCategory,
)
from src.core.category.application.usecases.list_category import (
    ListCategory,
)
from src.core.category.application.usecases.update_category import (
    UpdateCategory,
)
from src.django_project.category_app.repository import DjangoORMCategoryRepository
from src.django_project.category_app.serializers import (
    CreateCategoryDeserializer,
    CreateCategorySerializer,
    DeleteCategoryDeserializer,
    ListCategorySerializer,
    RetrieveCategoryDeserializer,
    RetrieveCategorySerializer,
    UpdateCategoryDeserializer,
)
from src.django_project.genre_app.serializers import ListEntityInputDeserializer


class CategoryViewSet(viewsets.ViewSet):
    def list(self, request: Request) -> Response:
        deserializer = ListEntityInputDeserializer(data=request.query_params)
        deserializer.is_valid(raise_exception=True)

        input = ListCategory.Input(**deserializer.validated_data)
        use_case = ListCategory(repository=DjangoORMCategoryRepository())

        output = use_case.execute(input)

        serializer = ListCategorySerializer(instance=output)
        return Response(status=HTTP_200_OK, data=serializer.data)

    def retrieve(self, request: Request, pk: None) -> Response:
        deserializer = RetrieveCategoryDeserializer(data={"id": pk})
        deserializer.is_valid(raise_exception=True)

        input = GetCategory.Input(id=deserializer.data.get("id"))
        use_case = GetCategory(repository=DjangoORMCategoryRepository())

        try:
            output = use_case.execute(input=input)
        except CategoryNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        serializer = RetrieveCategorySerializer(instance=output)
        return Response(
            status=HTTP_200_OK,
            data=serializer.data,
        )

    def create(self, request: Request) -> Response:
        deserializer = CreateCategoryDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        input = CreateCategory.Input(**deserializer.validated_data)
        use_case = CreateCategory(repository=DjangoORMCategoryRepository())

        output = use_case.execute(input=input)

        return Response(
            status=HTTP_201_CREATED,
            data=CreateCategorySerializer(instance=output).data,
        )

    def update(self, request: Request, pk: UUID = None):
        deserializer = UpdateCategoryDeserializer(
            data={
                **request.data,
                "id": pk,
            }
        )
        deserializer.is_valid(raise_exception=True)

        input = UpdateCategory.Input(**deserializer.validated_data)
        use_case = UpdateCategory(repository=DjangoORMCategoryRepository())
        try:
            use_case.execute(input=input)
        except CategoryNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request: Request, pk: UUID = None):
        deserializer = DeleteCategoryDeserializer(data={"id": pk})
        deserializer.is_valid(raise_exception=True)

        input = DeleteCategory.Input(**deserializer.validated_data)
        use_case = DeleteCategory(repository=DjangoORMCategoryRepository())
        try:
            use_case.execute(input)
        except CategoryNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)

    def partial_update(self, request, pk: UUID = None):
        deserializer = UpdateCategoryDeserializer(
            data={
                **request.data,
                "id": pk,
            },
            partial=True,
        )
        deserializer.is_valid(raise_exception=True)

        input = UpdateCategory.Input(**deserializer.validated_data)
        use_case = UpdateCategory(repository=DjangoORMCategoryRepository())
        try:
            use_case.execute(input=input)
        except CategoryNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)
