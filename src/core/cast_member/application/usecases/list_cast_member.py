from dataclasses import dataclass
from uuid import UUID
from src.core.cast_member.domain.cast_member import CastMemberType, CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


@dataclass
class ListCastMemberOutput:
    id: UUID
    name: str
    type: CastMemberType


@dataclass
class ListCastMemberRequest:
    pass


@dataclass
class ListCastMemberResponse:
    data: list[ListCastMemberOutput]


class ListCastMemberUseCase:

    def __init__(self, repository: ICastMemberRepository) -> None:
        self.repository = repository

    def execute(self, request: ListCastMemberRequest) -> ListCastMemberResponse:
        cast_members = self.repository.list()

        return ListCastMemberResponse(
            data=[
                ListCastMemberOutput(
                    id=cast_member.id, name=cast_member.name, type=cast_member.type
                )
                for cast_member in cast_members
            ]
        )
