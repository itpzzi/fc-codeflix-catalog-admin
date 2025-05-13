from uuid import UUID
from src.core.cast_member.application.exceptions import CastMemberNotFound
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository
from dataclasses import dataclass


@dataclass
class DeleteCastMemberInput:
    id: UUID


@dataclass
class DeleteCastMemberOutput:
    pass


class DeleteCastMember:
    def __init__(self, repository: ICastMemberRepository):
        self.repository = repository

    def execute(self, input: DeleteCastMemberInput) -> None:
        cast_member_from_repo = self.repository.get_by_id(input.id)

        if cast_member_from_repo is None:
            raise CastMemberNotFound(
                f"Cannot delete non-existent cast member. {input.id} not found"
            )

        self.repository.delete(cast_member_from_repo.id)
