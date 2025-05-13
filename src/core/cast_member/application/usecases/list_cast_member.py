from dataclasses import dataclass
from uuid import UUID
from src.core.cast_member.domain.cast_member import CastMemberType, CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


@dataclass
class ListCastMemberItem:
    id: UUID
    name: str
    type: CastMemberType


@dataclass
class ListCastMemberInput:
    pass


@dataclass
class ListCastMemberOutput:
    data: list[ListCastMemberItem]


class ListCastMemberUseCase:

    def __init__(self, repository: ICastMemberRepository) -> None:
        self.repository = repository

    def execute(self, input: ListCastMemberInput) -> ListCastMemberOutput:
        cast_members = self.repository.list()

        return ListCastMemberOutput(
            data=[
                ListCastMemberItem(
                    id=cast_member.id, name=cast_member.name, type=cast_member.type
                )
                for cast_member in cast_members
            ]
        )
