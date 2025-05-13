import uuid

import pytest
from core.cast_member.application.usecases.list_cast_member import (
    ListCastMemberOutput,
)
from src.core.cast_member.application.usecases.list_cast_member import (
    ListCastMemberOutput,
    ListCastMemberInput,
    ListCastMemberUseCase,
    ListCastMemberItem,
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


@pytest.fixture
def director_cast_member():
    return CastMember(
        name="Zombie",
        type=CastMemberType.DIRECTOR,
    )


class TestListCastMember:
    def test_list_all_the_cast_members(
        self, repository, actor_cast_member, director_cast_member
    ):
        repository.save(actor_cast_member)
        repository.save(director_cast_member)

        request = ListCastMemberInput()
        use_case = ListCastMemberUseCase(repository=repository)

        response = use_case.execute(request)

        assert response == ListCastMemberOutput(data=response.data)
        assert len(response.data) == 2
        assert response == ListCastMemberOutput(
            data=[
                ListCastMemberItem(
                    id=actor_cast_member.id,
                    name=actor_cast_member.name,
                    type=actor_cast_member.type,
                ),
                ListCastMemberItem(
                    id=director_cast_member.id,
                    name=director_cast_member.name,
                    type=director_cast_member.type,
                ),
            ]
        )

    def test_when_no_cast_members_then_return_empty_list(self):
        repository = InMemoryCastMemberRepository(cast_members=[])
        use_case = ListCastMemberUseCase(repository=repository)
        request = ListCastMemberInput()

        response = use_case.execute(request)

        assert len(response.data) == 0
        assert response == ListCastMemberOutput(data=[])
