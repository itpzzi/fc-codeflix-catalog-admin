from uuid import UUID
from rest_framework import viewsets

from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
)

from src.core.genre.application.exceptions import (
    GenreNotFound,
    InvalidGenre,
    RelatedCategoriesNotFound,
)
from src.django_project.category_app.repository import DjangoORMCategoryRepository
from src.django_project.genre_app.serializers import (
    CreateGenreRequestSerializer,
    CreateGenreResponseSerializer,
    DeleteGenreRequestSerializer,
    ListGenreResponseSerializer,
    UpdateGenreRequestSerializer,
)
from src.django_project.genre_app.repository import DjangoORMGenreRepository

from src.core.genre.application.usecases.list_genre import (
    ListGenre,
    ListGenreInput,
)
from src.core.genre.application.usecases.create_genre import (
    CreateGenre,
    CreateGenreInput,
)
from src.core.genre.application.usecases.delete_genre import (
    DeleteGenre,
    DeleteGenreInput,
)
from src.core.genre.application.usecases.update_genre import (
    UpdateGenre,
    UpdateGenreInput,
)


class GenreViewSet(viewsets.ViewSet):
    def list(self, request: Request) -> Response:
        input = ListGenreInput()
        use_case = ListGenre(repository=DjangoORMGenreRepository())

        output = use_case.execute(input)

        serializer = ListGenreResponseSerializer(instance=output)
        return Response(status=HTTP_200_OK, data=serializer.data)

    def create(self, request: Request) -> Response:
        deserializer = CreateGenreRequestSerializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        input = CreateGenreInput(**deserializer.validated_data)
        use_case = CreateGenre(
            repository=DjangoORMGenreRepository(),
            category_repository=DjangoORMCategoryRepository(),
        )

        try:
            output = use_case.execute(input=input)
        except (RelatedCategoriesNotFound, InvalidGenre) as error:
            return Response(status=HTTP_400_BAD_REQUEST, data={"error": str(error)})

        return Response(
            status=HTTP_201_CREATED,
            data=CreateGenreResponseSerializer(instance=output).data,
        )

    def update(self, request: Request, pk: UUID = None):
        deserializer = UpdateGenreRequestSerializer(
            data={
                **request.data,
                "id": pk,
            }
        )
        deserializer.is_valid(raise_exception=True)

        input = UpdateGenreInput(**deserializer.validated_data)
        use_case = UpdateGenre(
            repository=DjangoORMGenreRepository(),
            category_repository=DjangoORMCategoryRepository(),
        )
        try:
            use_case.execute(input=input)
        except GenreNotFound:
            return Response(status=HTTP_404_NOT_FOUND)
        except (RelatedCategoriesNotFound, InvalidGenre):
            return Response(status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request: Request, pk: UUID = None):
        deserializer = DeleteGenreRequestSerializer(data={"id": pk})
        deserializer.is_valid(raise_exception=True)

        input = DeleteGenreInput(**deserializer.validated_data)
        use_case = DeleteGenre(repository=DjangoORMGenreRepository())
        try:
            use_case.execute(input)
        except GenreNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)
