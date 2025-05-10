from unittest.mock import create_autospec
import uuid

import pytest
from src.core.cast_member.infra.in_memory_cast_member_repository import (
    InMemoryCastMemberRepository,
)
from src.core.cast_member.application.usecases.delete_cast_member import (
    DeleteCastMemberRequest,
    DeleteCastMemberUseCase,
)
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType


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


@pytest.fixture
def repository(actor_cast_member, director_cast_member):
    return InMemoryCastMemberRepository(
        cast_members=[actor_cast_member, director_cast_member]
    )


class TestDeleteCastMember:
    def test_should_delete_cast_member_from_repository(
        self, repository, director_cast_member
    ):
        use_case = DeleteCastMemberUseCase(repository=repository)
        cast_member_id = director_cast_member.id

        assert (
            repository.get_by_id(cast_member_id) is not None
        ), "Precondition failed: Cast member should exist"

        initial_count = len(repository.list())
        assert (
            initial_count == 2
        ), f"Expected 2 cast members before deletion, got {initial_count}"

        use_case.execute(DeleteCastMemberRequest(id=cast_member_id))

        assert (
            repository.get_by_id(cast_member_id) is None
        ), "Cast member was not deleted"
        remaining_count = len(repository.list())
        assert (
            remaining_count == 1
        ), f"Expected 1 cast member after deletion, got {remaining_count}"
