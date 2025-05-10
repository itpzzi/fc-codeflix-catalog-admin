import uuid
import pytest
from src.core.cast_member.domain.cast_member import CastMember, CastMemberType
from src.django_project.cast_member_app.repository import DjangoORMCastMemberRepository


@pytest.fixture
def cast_member_repository():
    return DjangoORMCastMemberRepository()


@pytest.fixture
def director_cast_member():
    return CastMember(name="Zombie", type=CastMemberType.DIRECTOR)


@pytest.fixture
def actor_cast_member():
    return CastMember(name="Steve", type=CastMemberType.ACTOR)


@pytest.fixture
def cast_member_repository_with_members(
    cast_member_repository, director_cast_member, actor_cast_member
):
    cast_member_repository.save(director_cast_member)
    cast_member_repository.save(actor_cast_member)
    return cast_member_repository


@pytest.mark.django_db
class TestSave:
    def test_can_save_cast_member(self, cast_member_repository, director_cast_member):
        assert len(cast_member_repository.list()) == 0
        cast_member_repository.save(director_cast_member)
        assert len(cast_member_repository.list()) == 1

        saved = cast_member_repository.get_by_id(director_cast_member.id)
        assert saved.id == director_cast_member.id
        assert saved.name == director_cast_member.name
        assert saved.type == director_cast_member.type
        assert saved.id is not None


@pytest.mark.django_db
class TestGet:
    def test_can_get_by_id(
        self, cast_member_repository_with_members, director_cast_member
    ):
        saved = cast_member_repository_with_members.get_by_id(director_cast_member.id)
        assert len(cast_member_repository_with_members.list()) == 2
        assert saved.id == director_cast_member.id
        assert saved.name == director_cast_member.name
        assert saved.type == director_cast_member.type

    def test_return_none_for_non_existent_id(self, cast_member_repository_with_members):
        fake_id = uuid.uuid4()

        saved = cast_member_repository_with_members.get_by_id(fake_id)
        assert len(cast_member_repository_with_members.list()) == 2
        assert saved is None


@pytest.mark.django_db
class TestDelete:
    def test_can_delete_cast_member(
        self, cast_member_repository_with_members, director_cast_member
    ):
        assert len(cast_member_repository_with_members.list()) == 2

        cast_member_repository_with_members.delete(director_cast_member.id)

        assert len(cast_member_repository_with_members.list()) == 1
        assert (
            cast_member_repository_with_members.get_by_id(director_cast_member.id)
            is None
        )


@pytest.mark.django_db
class TestUpdate:
    def test_can_update_cast_member(
        self, cast_member_repository_with_members, director_cast_member
    ):
        assert len(cast_member_repository_with_members.list()) == 2
        to_update_member = CastMember(
            id=director_cast_member.id,
            name="Skeleton",
            type=CastMemberType.DIRECTOR,
        )

        cast_member_repository_with_members.update(to_update_member)
        updated_member = cast_member_repository_with_members.get_by_id(
            director_cast_member.id
        )

        assert updated_member is not None
        assert updated_member.id == to_update_member.id
        assert updated_member.name == to_update_member.name
        assert updated_member.type == to_update_member.type

    def test_can_update_cast_member_type(
        self, cast_member_repository_with_members, director_cast_member
    ):
        to_update_member = CastMember(
            id=director_cast_member.id,
            name=director_cast_member.name,
            type=CastMemberType.ACTOR,  # Mudando o tipo de DIRECTOR para ACTOR
        )

        cast_member_repository_with_members.update(to_update_member)
        updated_member = cast_member_repository_with_members.get_by_id(
            director_cast_member.id
        )

        assert updated_member is not None
        assert updated_member.type == CastMemberType.ACTOR

    def test_update_nonexistent_member_does_nothing(
        self, cast_member_repository_with_members
    ):
        fake_id = uuid.uuid4()
        to_update_member = CastMember(
            id=fake_id, name="fake-name", type=CastMemberType.DIRECTOR
        )

        cast_member_repository_with_members.update(to_update_member)

        assert cast_member_repository_with_members.get_by_id(fake_id) is None
        assert len(cast_member_repository_with_members.list()) == 2

    def test_update_preserves_id(
        self, cast_member_repository_with_members, director_cast_member
    ):
        to_update_member = CastMember(
            id=director_cast_member.id,
            name="Skeleton",
            type=CastMemberType.DIRECTOR,
        )

        cast_member_repository_with_members.update(to_update_member)
        updated_member = cast_member_repository_with_members.get_by_id(
            director_cast_member.id
        )

        assert updated_member is not None
        assert updated_member.id == director_cast_member.id

    def test_multiple_updates_keep_only_last(
        self, cast_member_repository_with_members, director_cast_member
    ):
        _1st_update = CastMember(
            id=director_cast_member.id,
            name="Steve X",
            type=CastMemberType.DIRECTOR,
        )
        _2nd_update = CastMember(
            id=director_cast_member.id,
            name="Steve Y",
            type=CastMemberType.ACTOR,
        )

        cast_member_repository_with_members.update(_1st_update)
        cast_member_repository_with_members.update(_2nd_update)
        updated_member = cast_member_repository_with_members.get_by_id(
            director_cast_member.id
        )

        assert updated_member is not None
        assert updated_member.name == _2nd_update.name
        assert updated_member.type == _2nd_update.type


@pytest.mark.django_db
class TestList:
    def test_list_all_cast_members(
        self,
        cast_member_repository_with_members,
        director_cast_member,
        actor_cast_member,
    ):
        members = cast_member_repository_with_members.list()

        assert len(members) == 2

        member_ids = [m.id for m in members]
        assert director_cast_member.id in member_ids
        assert actor_cast_member.id in member_ids

    def test_returns_empty_list_for_empty_repository(self, cast_member_repository):
        members = cast_member_repository.list()

        assert len(members) == 0
        assert members == []
