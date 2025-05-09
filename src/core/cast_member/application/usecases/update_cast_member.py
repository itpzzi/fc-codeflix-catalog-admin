from dataclasses import dataclass
from uuid import UUID
from core.cast_member.application.exceptions import (
    CastMemberNotFound,
    InvalidCastMember,
)
from core.cast_member.domain.cast_member import CastMemberType
from core.cast_member.domain.cast_member_repository import ICastMemberRepository


@dataclass
class UpdateCastMemberRequest:
    id: UUID
    name: str
    type: CastMemberType


@dataclass
class UpdateCastMemberResponse:
    pass


class UpdateCastMemberUseCase:

    def __init__(self, repository: ICastMemberRepository):
        self.repository = repository

    def execute(self, request: UpdateCastMemberRequest) -> None:
        cast_member_from_repo = self.repository.get_by_id(request.id)

        if cast_member_from_repo is None:
            raise CastMemberNotFound(
                f"Cannot update non-existent cast member. {request.id} not found"
            )

        try:
            cast_member_from_repo.update_cast_member(request.name, request.type)
        except ValueError as error:
            raise InvalidCastMember(error)

        self.repository.update(cast_member=cast_member_from_repo)
