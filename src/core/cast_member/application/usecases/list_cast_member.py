from dataclasses import dataclass
from uuid import UUID

from src.core._shared.list_entity import ListEntityInput, ListEntityOutput
from src.core.cast_member.domain.cast_member import CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


@dataclass
class ListCastMemberItem:
    id: UUID
    name: str
    type: CastMemberType


class ListCastMember:
    Input = ListEntityInput
    Output = ListEntityOutput[ListCastMemberItem]

    def __init__(self, repository: ICastMemberRepository) -> None:
        self.repository = repository

    def execute(self, input: Input) -> Output:
        cast_members = self.repository.list()
        cast_member_items = [
            ListCastMemberItem(id=cm.id, name=cm.name, type=cm.type)
            for cm in cast_members
        ]

        return self.Output(input, cast_member_items)
