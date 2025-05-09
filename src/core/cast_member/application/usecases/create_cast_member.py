from uuid import UUID
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.application.exceptions import InvalidCastMember
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository
from dataclasses import dataclass


@dataclass
class CreateCastMemberRequest:
    name: str
    type: CastMemberType


@dataclass
class CreateCastMemberResponse:
    id: UUID


class CreateCastMemberUseCase:
    def __init__(self, repository: ICastMemberRepository):
        self.repository = repository

    def execute(self, request: CreateCastMemberRequest) -> CreateCastMemberResponse:
        try:
            cast_member = CastMember(
                name=request.name,
                type=request.type,
            )
        except ValueError as error:
            raise InvalidCastMember(error)

        self.repository.save(cast_member)
        return CreateCastMemberResponse(id=cast_member.id)
