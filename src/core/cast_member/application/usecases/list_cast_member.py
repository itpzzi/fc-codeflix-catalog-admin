from dataclasses import dataclass
from uuid import UUID

from src.core.cast_member.domain.cast_member import CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


@dataclass
class ListCastMemberItem:
    id: UUID
    name: str
    type: CastMemberType


class ListCastMember:

    @dataclass
    class Input:
        pass

    @dataclass
    class Output:
        data: list[ListCastMemberItem]

    def __init__(self, repository: ICastMemberRepository) -> None:
        self.repository = repository

    def execute(self, input: Input) -> Output:
        cast_members = self.repository.list()

        return ListCastMember.Output(
            data=[
                ListCastMemberItem(
                    id=cast_member.id, name=cast_member.name, type=cast_member.type
                )
                for cast_member in cast_members
            ]
        )
