from uuid import UUID

from rest_framework import status, viewsets
from rest_framework.request import Request
from rest_framework.response import Response

from core.cast_member.application.usecases.create_cast_member import (
    CreateCastMember,
)
from core.cast_member.application.usecases.delete_cast_member import (
    DeleteCastMember,
)
from core.cast_member.application.usecases.list_cast_member import (
    ListCastMember,
)
from core.cast_member.application.usecases.update_cast_member import (
    UpdateCastMember,
)
from django_project.cast_member_app.repository import DjangoORMCastMemberRepository
from django_project.cast_member_app.serializers import (
    CreateCastMemberRequestSerializer,
    CreateCastMemberResponseSerializer,
    DeleteCastMemberRequestSerializer,
    ListCastMemberResponseSerializer,
    UpdateCastMemberRequestSerializer,
)
from src.core.cast_member.application.exceptions import (
    CastMemberNotFound,
    InvalidCastMember,
)


class CastMemberViewSet(viewsets.ViewSet):

    def create(self, request: Request) -> Response:
        deserializer = CreateCastMemberRequestSerializer(data=request.data)
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
            data=CreateCastMemberResponseSerializer(instance=output).data,
        )

    def list(self, request: Request) -> Response:
        input = ListCastMember.Input()
        use_case = ListCastMember(repository=DjangoORMCastMemberRepository())

        output = use_case.execute(input=input)

        serializer = ListCastMemberResponseSerializer(instance=output)

        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request: Request, pk: UUID = None):
        deserializer = DeleteCastMemberRequestSerializer(data={"id": pk})
        deserializer.is_valid(raise_exception=True)

        input = DeleteCastMember.Input(**deserializer.validated_data)
        use_case = DeleteCastMember(repository=DjangoORMCastMemberRepository())

        try:
            use_case.execute(input=input)
        except CastMemberNotFound:
            return Response(status=status.HTTP_404_NOT_FOUND)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request: Request, pk: UUID = None):
        deserializer = UpdateCastMemberRequestSerializer(
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
