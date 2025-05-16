from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from src.core.video.application.exceptions import InvalidVideo, RelatedEntitiesNotFound
from src.core.video.application.usecases.create_video_without_media import (
    CreateVideoWithoutMedia,
)
from src.django_project.cast_member_app.repository import DjangoORMCastMemberRepository
from src.django_project.category_app.repository import DjangoORMCategoryRepository
from src.django_project.genre_app.repository import DjangoORMGenreRepository
from src.django_project.video_app.repository import DjangoORMVideoRepository
from src.django_project.video_app.serializers import (
    CreateVideoWithoutMediaDeserializer,
    CreateVideoWithoutMediaSerializer,
)

category_repository = DjangoORMCategoryRepository()
genre_repository = DjangoORMGenreRepository()
cast_member_repository = DjangoORMCastMemberRepository()
video_repository = DjangoORMVideoRepository()


class VideoViewSet(viewsets.ViewSet):
    def create(self, request: Request) -> Response:
        deserializer = CreateVideoWithoutMediaDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        input = CreateVideoWithoutMedia.Input(**deserializer.validated_data)
        use_case = CreateVideoWithoutMedia(
            video_repository=video_repository,
            category_repository=category_repository,
            genre_repository=genre_repository,
            cast_member_repository=cast_member_repository,
        )

        try:
            output = use_case.execute(input=input)
        except (RelatedEntitiesNotFound, InvalidVideo) as error:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"error": str(error)}
            )

        serializer = CreateVideoWithoutMediaSerializer(instance=output)
        return Response(status=status.HTTP_201_CREATED, data=serializer.data)

    def update(self, request: Request, pk: str) -> Response:
        pass

    def partial_update(self, request: Request, pk: str) -> Response:
        pass

    def destroy(self, request: Request, pk: str) -> Response:
        pass
