import uuid
import pytest
from unittest.mock import create_autospec
from src.core.cast_member.application.exceptions import (
    CastMemberNotFound,
    InvalidCastMember,
)
from src.core.cast_member.application.usecases.update_cast_member import (
    UpdateCastMemberInput,
    UpdateCastMemberUseCase,
)
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository


@pytest.fixture
def mock_repository():
    return create_autospec(ICastMemberRepository)


@pytest.fixture
def mock_cast_member():
    return CastMember(
        id=uuid.uuid4(),
        name="Steve",
        type=CastMemberType.ACTOR,
    )


class TestUpdateCastMember:
    def test_raise_exception_when_cast_member_not_found(self, mock_repository):
        mock_repository.get_by_id.return_value = None
        use_case = UpdateCastMemberUseCase(repository=mock_repository)
        fake_id = "non-existent-id"

        request = UpdateCastMemberInput(id=fake_id, name="Any Name", type="actor")

        with pytest.raises(CastMemberNotFound) as exc:
            use_case.execute(request)

        mock_repository.update.assert_not_called()
        assert fake_id in str(exc.value)

    def test_raise_exception_with_invalid_payload(
        self, mock_repository, mock_cast_member
    ):
        mock_repository.get_by_id.return_value = mock_cast_member
        use_case = UpdateCastMemberUseCase(repository=mock_repository)

        request = UpdateCastMemberInput(
            id=mock_cast_member.id, name="", type="invalid-type"
        )

        with pytest.raises(InvalidCastMember):
            use_case.execute(request)

        mock_repository.update.assert_not_called()

    def test_update_cast_member_with_valid_payload(
        self, mock_repository, mock_cast_member
    ):
        mock_repository.get_by_id.return_value = mock_cast_member
        use_case = UpdateCastMemberUseCase(repository=mock_repository)

        request = UpdateCastMemberInput(
            id=mock_cast_member.id, name="Zombie", type=CastMemberType.DIRECTOR
        )

        use_case.execute(request)

        assert mock_cast_member.name == "Zombie"
        assert mock_cast_member.type == CastMemberType.DIRECTOR
        mock_repository.update.assert_called_once_with(mock_cast_member)
