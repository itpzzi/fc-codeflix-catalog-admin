from uuid import UUID

from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from src.core.cast_member.application.exceptions import (
    CastMemberNotFound,
    InvalidCastMember,
)
from src.core.cast_member.application.usecases.create_cast_member import (
    CreateCastMember,
)
from src.core.cast_member.application.usecases.delete_cast_member import (
    DeleteCastMember,
)
from src.core.cast_member.application.usecases.list_cast_member import (
    ListCastMember,
)
from src.core.cast_member.application.usecases.update_cast_member import (
    UpdateCastMember,
)
from src.django_project.cast_member_app.repository import DjangoORMCastMemberRepository
from src.django_project.cast_member_app.serializers import (
    CreateCastMemberDeserializer,
    CreateCastMemberSerializer,
    DeleteCastMemberDeserializer,
    ListCastMemberSerializer,
    UpdateCastMemberDeserializer,
)
from src.django_project.genre_app.serializers import ListEntityInputDeserializer
from src.django_project.permissions import IsAdmin, IsAuthenticated


class CastMemberViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated | IsAdmin]

    def create(self, request: Request) -> Response:
        deserializer = CreateCastMemberDeserializer(data=request.data)
        deserializer.is_valid(raise_exception=True)

        input = CreateCastMember.Input(**deserializer.validated_data)
        use_case = CreateCastMember(repository=DjangoORMCastMemberRepository())

        try:
            output = use_case.execute(input=input)
        except InvalidCastMember as error:
            return Response(
                status=status.HTTP_400_BAD_REQUEST, data={"error": str(error)}
            )

        return Response(
            status=status.HTTP_201_CREATED,
            data=CreateCastMemberSerializer(instance=output).data,
        )

    def list(self, request: Request) -> Response:
        deserializer = ListEntityInputDeserializer(data=request.query_params)
        deserializer.is_valid(raise_exception=True)

        input = ListCastMember.Input(**deserializer.validated_data)
        use_case = ListCastMember(repository=DjangoORMCastMemberRepository())

        output = use_case.execute(input=input)

        serializer = ListCastMemberSerializer(instance=output)

        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request: Request, pk: UUID = None):
        deserializer = DeleteCastMemberDeserializer(data={"id": pk})
        deserializer.is_valid(raise_exception=True)

        input = DeleteCastMember.Input(**deserializer.validated_data)
        use_case = DeleteCastMember(repository=DjangoORMCastMemberRepository())

        try:
            use_case.execute(input=input)
        except CastMemberNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request: Request, pk: UUID = None):
        deserializer = UpdateCastMemberDeserializer(
            data={
                **request.data,
                "id": pk,
            }
        )
        deserializer.is_valid(raise_exception=True)

        input = UpdateCastMember.Input(**deserializer.validated_data)
        use_case = UpdateCastMember(repository=DjangoORMCastMemberRepository())

        try:
            use_case.execute(input=input)
        except CastMemberNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)
