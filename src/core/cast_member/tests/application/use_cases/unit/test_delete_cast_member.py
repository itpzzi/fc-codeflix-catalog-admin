from unittest.mock import create_autospec

import pytest

from src.core.cast_member.application.exceptions import CastMemberNotFound
from src.core.cast_member.application.usecases.delete_cast_member import (
    DeleteCastMember,
)
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


@pytest.fixture
def actor_cast_member():
    return CastMember(name="Steve", type=CastMemberType.ACTOR)


@pytest.fixture
def mock_repository():
    return create_autospec(ICastMemberRepository)


class TestDeleteCastMember:
    def test_should_delete_existing_cast_member(
        self, mock_repository, actor_cast_member
    ):
        mock_repository.get_by_id.return_value = actor_cast_member
        input = DeleteCastMember.Input(id=actor_cast_member.id)
        use_case = DeleteCastMember(repository=mock_repository)

        use_case.execute(input=input)

        mock_repository.delete.assert_called_once_with(actor_cast_member.id)

    def test_should_raise_exception_when_cast_member_not_found(
        self, mock_repository, actor_cast_member
    ):
        mock_repository.get_by_id.return_value = None
        input = DeleteCastMember.Input(id=actor_cast_member.id)
        use_case = DeleteCastMember(repository=mock_repository)

        with pytest.raises(CastMemberNotFound) as exc:
            use_case.execute(input=input)

        mock_repository.delete.assert_not_called()
        assert str(actor_cast_member.id) in str(exc.value)
