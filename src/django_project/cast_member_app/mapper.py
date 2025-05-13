from src.core.cast_member.domain.cast_member import CastMember
from src.django_project.cast_member_app.models import CastMember as CastMemberModel


class CastMemberModelMapper:
    @staticmethod
    def to_entity(model: CastMemberModel) -> CastMember:
        return CastMember(
            id=model.id,
            name=model.name,
            type=model.type,
        )

    @staticmethod
    def to_model(cast_member: CastMember) -> CastMemberModel:
        model = CastMemberModel(
            id=cast_member.id,
            name=cast_member.name,
            type=cast_member.type,
        )
        return model
