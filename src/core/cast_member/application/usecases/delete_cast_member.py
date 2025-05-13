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


class DeleteCastMemberUseCase:
    def __init__(self, repository: ICastMemberRepository):
        self.repository = repository

    def execute(self, request: DeleteCastMemberInput) -> None:
        cast_member_from_repo = self.repository.get_by_id(request.id)

        if cast_member_from_repo is None:
            raise CastMemberNotFound(
                f"Cannot delete non-existent cast member. {request.id} not found"
            )

        self.repository.delete(cast_member_from_repo.id)
