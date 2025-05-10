import uuid
import pytest
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.core.cast_member.domain.cast_member_repository import ICastMemberRepository
from src.core.cast_member.infra.in_memory_cast_member_repository import (
    InMemoryCastMemberRepository,
)


# -------------------- Fixtures -------------------- #


@pytest.fixture
def cast_member_repository() -> ICastMemberRepository:
    return InMemoryCastMemberRepository()


@pytest.fixture
def actor_cast_member() -> CastMember:
    return CastMember(name="Steve", type=CastMemberType.ACTOR)


@pytest.fixture
def director_cast_member() -> CastMember:
    return CastMember(name="Zombie", type=CastMemberType.DIRECTOR)


# -------------------- Testes de criação -------------------- #


class TestCreateCastMember:
    def test_can_save_cast_member(self, cast_member_repository, actor_cast_member):
        cast_member_repository.save(actor_cast_member)

        saved = cast_member_repository.list()
        assert len(saved) == 1
        assert saved[0] == actor_cast_member


# -------------------- Testes de obtenção -------------------- #


class TestGetCastMember:
    def test_can_get_by_id(
        self, cast_member_repository, actor_cast_member, director_cast_member
    ):
        cast_member_repository.save(actor_cast_member)
        cast_member_repository.save(director_cast_member)

        result = cast_member_repository.get_by_id(director_cast_member.id)
        assert result is not None
        assert result.name == "Zombie"
        assert result.type == CastMemberType.DIRECTOR

    def test_returns_none_for_nonexistent_id(self, cast_member_repository):
        fake_id = uuid.uuid4()
        result = cast_member_repository.get_by_id(fake_id)
        assert result is None


# -------------------- Testes de remoção -------------------- #


class TestDeleteCastMember:
    def test_can_delete_cast_member(
        self, cast_member_repository, actor_cast_member, director_cast_member
    ):
        cast_member_repository.save(actor_cast_member)
        cast_member_repository.save(director_cast_member)

        cast_member_repository.delete(actor_cast_member.id)

        remaining = cast_member_repository.list()
        assert len(remaining) == 1
        assert remaining[0].id == director_cast_member.id


# -------------------- Testes de atualização -------------------- #


class TestUpdateCastMember:
    def test_can_update_cast_member(self, cast_member_repository, actor_cast_member):
        cast_member_repository.save(actor_cast_member)

        updated = CastMember(
            id=actor_cast_member.id, name="Updated Steve", type=CastMemberType.DIRECTOR
        )
        cast_member_repository.update(updated)

        result = cast_member_repository.get_by_id(actor_cast_member.id)
        assert result.name == "Updated Steve"
        assert result.type == CastMemberType.DIRECTOR

    def test_update_nonexistent_member_does_nothing(self, cast_member_repository):
        member = CastMember(id=uuid.uuid4(), name="Ghost", type=CastMemberType.ACTOR)
        cast_member_repository.update(member)

        assert cast_member_repository.get_by_id(member.id) is None

    def test_update_preserves_id(self, cast_member_repository, director_cast_member):
        cast_member_repository.save(director_cast_member)

        updated = CastMember(
            id=director_cast_member.id,
            name="Fresh Zombie",
            type=CastMemberType.DIRECTOR,
        )
        cast_member_repository.update(updated)

        result = cast_member_repository.get_by_id(director_cast_member.id)
        assert result.id == director_cast_member.id
        assert result.name == "Fresh Zombie"

    def test_multiple_updates_keep_last(
        self, cast_member_repository, actor_cast_member
    ):
        cast_member_repository.save(actor_cast_member)

        update1 = CastMember(
            id=actor_cast_member.id, name="Steve One", type=CastMemberType.ACTOR
        )
        update2 = CastMember(
            id=actor_cast_member.id, name="Final Steve", type=CastMemberType.DIRECTOR
        )

        cast_member_repository.update(update1)
        cast_member_repository.update(update2)

        result = cast_member_repository.get_by_id(actor_cast_member.id)
        assert result.name == "Final Steve"
        assert result.type == CastMemberType.DIRECTOR


# -------------------- Testes de listagem -------------------- #


class TestListCastMember:
    def test_list_returns_all_saved_cast_members(
        self, cast_member_repository, actor_cast_member, director_cast_member
    ):
        cast_member_repository.save(actor_cast_member)
        cast_member_repository.save(director_cast_member)

        members = cast_member_repository.list()
        assert len(members) == 2
        assert actor_cast_member in members
        assert director_cast_member in members
