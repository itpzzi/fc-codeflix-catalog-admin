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
    ListGenreUseCase,
    ListGenreRequest,
)
from src.core.genre.application.usecases.create_genre import (
    CreateGenreUseCase,
    CreateGenreRequest,
)
from src.core.genre.application.usecases.delete_genre import (
    DeleteGenreUseCase,
    DeleteGenreRequest,
)
from src.core.genre.application.usecases.update_genre import (
    UpdateGenreUseCase,
    UpdateGenreRequest,
)


class GenreViewSet(viewsets.ViewSet):
    def list(self, request: Request) -> Response:
        input = ListGenreRequest()
        use_case = ListGenreUseCase(repository=DjangoORMGenreRepository())

        output = use_case.execute(input)

        serializer = ListGenreResponseSerializer(instance=output)
        return Response(status=HTTP_200_OK, data=serializer.data)

    def create(self, request: Request) -> Response:
        deserializer = CreateGenreRequestSerializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        input = CreateGenreRequest(**deserializer.validated_data)
        use_case = CreateGenreUseCase(
            repository=DjangoORMGenreRepository(),
            category_repository=DjangoORMCategoryRepository(),
        )

        try:
            output = use_case.execute(request=input)
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

        input = UpdateGenreRequest(**deserializer.validated_data)
        use_case = UpdateGenreUseCase(
            repository=DjangoORMGenreRepository(),
            category_repository=DjangoORMCategoryRepository(),
        )
        try:
            use_case.execute(request=input)
        except GenreNotFound:
            return Response(status=HTTP_404_NOT_FOUND)
        except (RelatedCategoriesNotFound, InvalidGenre):
            return Response(status=HTTP_400_BAD_REQUEST)

        return Response(status=HTTP_204_NO_CONTENT)

    def destroy(self, request: Request, pk: UUID = None):
        deserializer = DeleteGenreRequestSerializer(data={"id": pk})
        deserializer.is_valid(raise_exception=True)

        input = DeleteGenreRequest(**deserializer.validated_data)
        use_case = DeleteGenreUseCase(repository=DjangoORMGenreRepository())
        try:
            use_case.execute(input)
        except GenreNotFound:
            return Response(status=HTTP_404_NOT_FOUND)

        return Response(status=HTTP_204_NO_CONTENT)
