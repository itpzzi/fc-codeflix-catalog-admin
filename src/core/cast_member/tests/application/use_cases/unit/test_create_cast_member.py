import pytest
from unittest.mock import create_autospec
from uuid import UUID
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository
from src.core.cast_member.application.exceptions import InvalidCastMember
from src.core.cast_member.application.usecases.create_cast_member import (
    CreateCastMember,
)


@pytest.fixture
def mock_repository():
    return create_autospec(ICastMemberRepository)


@pytest.fixture
def actor_cast_member():
    return CastMember(name="Steve", type=CastMemberType.ACTOR)


class TestCreateCastMember:
    def test_should_raise_exception_when_cast_member_is_invalid(self, mock_repository):
        use_case = CreateCastMember(repository=mock_repository)
        input = CreateCastMember.Input(name="", type=CastMemberType.ACTOR)  # inválido

        with pytest.raises(InvalidCastMember) as exc:
            use_case.execute(input=input)

        mock_repository.save.assert_not_called()
        assert "name cannot be empty" in str(exc.value)

    def test_should_create_cast_member_when_input_is_valid(self, mock_repository):
        use_case = CreateCastMember(repository=mock_repository)
        input = CreateCastMember.Input(name="Steve", type=CastMemberType.ACTOR)

        output = use_case.execute(input=input)

        assert isinstance(output, CreateCastMember.Output)
        assert isinstance(output.id, UUID)
        mock_repository.save.assert_called_once()
