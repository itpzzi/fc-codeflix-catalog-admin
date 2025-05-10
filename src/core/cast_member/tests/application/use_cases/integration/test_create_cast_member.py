from uuid import UUID
import pytest

from core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.infra.in_memory_cast_member_repository import (
    InMemoryCastMemberRepository,
)

from src.core.cast_member.application.usecases.create_cast_member import (
    CreateCastMemberRequest,
    CreateCastMemberResponse,
    CreateCastMemberUseCase,
)


@pytest.fixture
def repository():
    return InMemoryCastMemberRepository(cast_members=[])


@pytest.fixture
def actor_cast_member():
    return CastMember(
        name="Steve",
        type=CastMemberType.ACTOR,
    )


class TestCreateCastMember:
    def test_create_cast_member_with_valid_payload(
        self,
        repository,
        actor_cast_member
    ):
        use_case = CreateCastMemberUseCase(
            repository=repository
        )

        output = use_case.execute(
            CreateCastMemberRequest(
                name=actor_cast_member.name,
                type=actor_cast_member.type
            )
        )

        created_cast_member = repository.get_by_id(output.id)
        assert output == CreateCastMemberResponse(id=output.id)
        assert created_cast_member is not None
        assert created_cast_member.name == "Steve"
        assert created_cast_member.type == CastMemberType.ACTOR