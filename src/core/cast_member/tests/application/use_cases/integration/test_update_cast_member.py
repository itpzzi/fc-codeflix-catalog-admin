import uuid

import pytest
from src.core.cast_member.application.usecases.update_cast_member import (
    UpdateCastMemberInput,
    UpdateCastMemberUseCase,
)
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.infra.in_memory_cast_member_repository import (
    InMemoryCastMemberRepository,
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


class TestUpdateCastMember:
    def test_can_update_cast_member_name_and_type(self, repository, actor_cast_member):
        repository.save(actor_cast_member)
        use_case = UpdateCastMemberUseCase(repository=repository)
        request = UpdateCastMemberInput(
            id=actor_cast_member.id, name="Zombie", type=CastMemberType.DIRECTOR
        )

        use_case.execute(request)

        updated_cast_member = repository.get_by_id(actor_cast_member.id)
        assert updated_cast_member is not None
        assert updated_cast_member.name == "Zombie"
        assert updated_cast_member.type == CastMemberType.DIRECTOR
