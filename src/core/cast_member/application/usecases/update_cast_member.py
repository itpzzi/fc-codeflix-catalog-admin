from dataclasses import dataclass
from uuid import UUID

from src.core.cast_member.application.exceptions import (
    CastMemberNotFound,
    InvalidCastMember,
)
from src.core.cast_member.domain.cast_member import CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


class UpdateCastMember:

    @dataclass
    class Input:
        id: UUID
        name: str
        type: CastMemberType

    @dataclass
    class Output:
        pass

    def __init__(self, repository: ICastMemberRepository):
        self.repository = repository

    def execute(self, input: Input) -> None:
        cast_member_from_repo = self.repository.get_by_id(input.id)

        if cast_member_from_repo is None:
            raise CastMemberNotFound(
                f"Cannot update non-existent cast member. {input.id} not found"
            )

        try:
            cast_member_from_repo.update_cast_member(input.name, input.type)
        except ValueError as error:
            raise InvalidCastMember(error)

        self.repository.update(cast_member=cast_member_from_repo)
