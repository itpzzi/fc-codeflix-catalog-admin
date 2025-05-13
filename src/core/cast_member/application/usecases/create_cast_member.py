from dataclasses import dataclass
from uuid import UUID

from src.core.cast_member.application.exceptions import InvalidCastMember
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


class CreateCastMember:

    @dataclass
    class Input:
        name: str
        type: CastMemberType

    @dataclass
    class Output:
        id: UUID

    def __init__(self, repository: ICastMemberRepository):
        self.repository = repository

    def execute(self, input: Input) -> Output:
        try:
            cast_member = CastMember(
                name=input.name,
                type=input.type,
            )
        except ValueError as error:
            raise InvalidCastMember(error)

        self.repository.save(cast_member)
        return CreateCastMember.Output(id=cast_member.id)
