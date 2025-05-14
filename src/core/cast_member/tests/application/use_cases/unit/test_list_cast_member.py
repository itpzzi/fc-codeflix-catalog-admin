import random
from unittest.mock import create_autospec

import pytest

from src.core._shared.config import DEFAULT_PAGE_SIZE
from src.core.cast_member.application.usecases.list_cast_member import (
    ListCastMember,
    ListCastMemberItem,
)
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


@pytest.fixture
def mock_repository():
    return create_autospec(ICastMemberRepository)


@pytest.fixture
def mock_cast_members():
    return [
        CastMember(name="A", type=CastMemberType.ACTOR),
        CastMember(name="B", type=CastMemberType.DIRECTOR),
        CastMember(name="C", type=CastMemberType.DIRECTOR),
        CastMember(name="D", type=CastMemberType.ACTOR),
    ]


@pytest.fixture
def shuffled_cast_members(mock_cast_members):
    shuffled = mock_cast_members[:]
    random.shuffle(shuffled)
    return shuffled


class TestListCastMember:
    def test_list_all_cast_members(self, mock_repository, mock_cast_members):
        mock_repository.list.return_value = mock_cast_members
        input = ListCastMember.Input(per_page=4)
        use_case = ListCastMember(repository=mock_repository)

        expected_data = [
            ListCastMemberItem(id=cm.id, name=cm.name, type=cm.type)
            for cm in mock_cast_members
        ]

        output = use_case.execute(input=input)

        assert output.data == expected_data
        assert output.meta.total == 4
        assert output.meta.current_page == 1
        assert output.meta.per_page == 4

    def test_list_empty_repository(self, mock_repository):
        mock_repository.list.return_value = []
        input = ListCastMember.Input()
        use_case = ListCastMember(repository=mock_repository)

        output = use_case.execute(input=input)

        assert output.data == []
        assert output.meta.total == 0
        assert output.meta.current_page == 1
        assert output.meta.per_page == 2

    @pytest.mark.parametrize(
        "order_by, reverse, current_page, per_page, expected_names",
        [
            ("name", False, 1, DEFAULT_PAGE_SIZE, ["A", "B"]),
            ("name", False, 2, DEFAULT_PAGE_SIZE, ["C", "D"]),
            ("name", True, 1, DEFAULT_PAGE_SIZE, ["D", "C"]),
            ("name", True, 2, DEFAULT_PAGE_SIZE, ["B", "A"]),
        ],
    )
    def test_list_with_ordering_and_pagination(
        self,
        mock_repository,
        mock_cast_members,
        order_by,
        reverse,
        current_page,
        per_page,
        expected_names,
    ):
        mock_repository.list.return_value = mock_cast_members
        input = ListCastMember.Input(
            order_by=order_by,
            reverse=reverse,
            current_page=current_page,
            per_page=per_page,
        )
        use_case = ListCastMember(repository=mock_repository)

        sorted_members = sorted(
            mock_cast_members,
            key=lambda x: getattr(x, order_by),
            reverse=reverse,
        )
        paged = sorted_members[(current_page - 1) * per_page : current_page * per_page]
        expected_data = [
            ListCastMemberItem(id=cm.id, name=cm.name, type=cm.type) for cm in paged
        ]

        output = use_case.execute(input=input)

        assert [cm.name for cm in output.data] == expected_names
        assert output.data == expected_data
        assert output.meta.total == len(mock_cast_members)
        assert output.meta.current_page == current_page
        assert output.meta.per_page == per_page
