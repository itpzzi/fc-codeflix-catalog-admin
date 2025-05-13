from uuid import UUID

from src.core.cast_member.domain.cast_member import CastMember
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository
from src.django_project.cast_member_app.models import CastMember as CastMemberModel


class DjangoORMCastMemberRepository(ICastMemberRepository):
    def __init__(self, model: CastMemberModel = CastMemberModel):
        self.model = model

    def save(self, cast_member: CastMember) -> None:
        self.model.objects.create(
            id=cast_member.id,
            name=cast_member.name,
            type=cast_member.type,
        )

    def get_by_id(self, id: UUID) -> CastMember | None:
        try:
            cast_member_model = self.model.objects.get(pk=id)

            return CastMember(
                id=cast_member_model.id,
                name=cast_member_model.name,
                type=cast_member_model.type,
            )
        except self.model.DoesNotExist:
            return None

    def delete(self, id: UUID) -> None:
        self.model.objects.filter(id=id).delete()

    def update(self, cast_member: CastMember) -> None:
        try:
            self.model.objects.get(pk=cast_member.id)
        except self.model.DoesNotExist:
            return None

        self.model.objects.filter(pk=cast_member.id).update(
            name=cast_member.name,
            type=cast_member.type,
        )

    def list(self) -> list[CastMember]:
        return [
            CastMember(
                id=cast_member_model.id,
                name=cast_member_model.name,
                type=cast_member_model.type,
            )
            for cast_member_model in self.model.objects.all()
        ]
