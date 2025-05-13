import pytest
from unittest.mock import create_autospec
from core.cast_member.application.usecases.list_cast_member import (
    ListCastMemberItem,
    ListCastMemberInput,
    ListCastMemberOutput,
    ListCastMemberUseCase,
)
from core.cast_member.domain.cast_member import CastMember, CastMemberType
from core.cast_member.domain.cast_member_repository import ICastMemberRepository


@pytest.fixture
def actor_cast_member():
    return CastMember(name="Steve", type=CastMemberType.ACTOR)


@pytest.fixture
def director_cast_member():
    return CastMember(name="Zombie", type=CastMemberType.DIRECTOR)


@pytest.fixture
def mock_repository():
    return create_autospec(ICastMemberRepository)


@pytest.fixture
def repository_with_two_cast_members(
    mock_repository, actor_cast_member, director_cast_member
):
    mock_repository.list.return_value = [actor_cast_member, director_cast_member]
    return mock_repository


class TestListCastMember:
    def test_list_all_cast_members(
        self,
        repository_with_two_cast_members,
        actor_cast_member,
        director_cast_member,
    ):
        input = ListCastMemberInput()
        use_case = ListCastMemberUseCase(repository=repository_with_two_cast_members)
        expected_data = [
            ListCastMemberItem(
                id=cast_member.id,
                name=cast_member.name,
                type=cast_member.type,
            )
            for cast_member in [actor_cast_member, director_cast_member]
        ]

        output = use_case.execute(input=input)

        assert output == ListCastMemberOutput(data=expected_data)
        assert len(output.data) == 2

    def test_return_empty_list_when_repository_is_empty(self, mock_repository):
        mock_repository.list.return_value = []
        input = ListCastMemberInput()
        use_case = ListCastMemberUseCase(repository=mock_repository)

        output = use_case.execute(input=input)

        assert output == ListCastMemberOutput(data=[])
        assert len(output.data) == 0
