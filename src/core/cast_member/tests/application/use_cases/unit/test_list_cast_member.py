from unittest.mock import create_autospec

import pytest

from src.core.cast_member.application.usecases.list_cast_member import (
    ListCastMember,
    ListCastMemberItem,
)
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


@pytest.fixture
def mock_cast_member_steve():
    return CastMember(name="Steve", type=CastMemberType.ACTOR)


@pytest.fixture
def mock_cast_member_zombie():
    return CastMember(name="Zombie", type=CastMemberType.DIRECTOR)


@pytest.fixture
def mock_repository():
    return create_autospec(ICastMemberRepository)


@pytest.fixture
def mock_repository_with_cast_members(
    mock_repository, mock_cast_member_steve, mock_cast_member_zombie
):
    mock_repository.list.return_value = [
        mock_cast_member_steve,
        mock_cast_member_zombie,
    ]
    return mock_repository


class TestListCastMember:
    def test_list_all_cast_members(
        self,
        mock_cast_member_steve,
        mock_cast_member_zombie,
        mock_repository_with_cast_members,
    ):
        input = ListCastMember.Input()
        use_case = ListCastMember(repository=mock_repository_with_cast_members)
        expected_data = [
            ListCastMemberItem(
                id=cast_member.id,
                name=cast_member.name,
                type=cast_member.type,
            )
            for cast_member in [mock_cast_member_steve, mock_cast_member_zombie]
        ]

        output = use_case.execute(input=input)

        assert output == ListCastMember.Output(data=expected_data)
        assert len(output.data) == 2

    def test_list_empty_list_for_an_empty_repository(self, mock_repository):
        empty_repository = mock_repository
        input = ListCastMember.Input()
        use_case = ListCastMember(repository=empty_repository)
        expected_data = []

        output = use_case.execute(input=input)

        assert output == ListCastMember.Output(data=expected_data)
