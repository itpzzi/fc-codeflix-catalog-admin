import pytest

from src.core.cast_member.application.usecases.list_cast_member import (
    ListCastMember,
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

        input = ListCastMember.Input()
        use_case = ListCastMember(repository=repository)

        output = use_case.execute(input=input)

        assert output.data == ListCastMember.Output(input, data=output.data).data
        assert output.data == [
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
        assert len(output.data) == 2
        assert output.meta.total == 2
        assert output.meta.current_page == 1
        assert output.meta.per_page == 2

    def test_when_no_cast_members_then_return_empty_list(self):
        repository = InMemoryCastMemberRepository(cast_members=[])
        use_case = ListCastMember(repository=repository)
        input = ListCastMember.Input()

        output = use_case.execute(input=input)

        assert output.data == ListCastMember.Output(input, data=output.data).data
        assert len(output.data) == 0
        assert output.meta.total == 0
        assert output.meta.current_page == 1
        assert output.meta.per_page == 2
