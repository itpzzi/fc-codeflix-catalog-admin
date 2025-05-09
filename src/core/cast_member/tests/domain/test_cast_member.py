import uuid
from uuid import UUID

import pytest

from src.core.cast_member.domain.cast_member import CastMember, CastMemberType


@pytest.fixture
def valid_name():
    return "Steve"


@pytest.fixture
def valid_id():
    return uuid.uuid4()


@pytest.fixture
def valid_type():
    return CastMemberType.ACTOR


@pytest.fixture
def valid_cast_member(valid_id, valid_name, valid_type):
    return CastMember(
        id=valid_id,
        name=valid_name,
        type=valid_type,
    )


class TestCastMember:
    def test_creates_cast_member_with_valid_data(
        self, valid_id, valid_name, valid_type, valid_cast_member
    ):
        cast_member = valid_cast_member

        assert isinstance(cast_member.id, UUID)
        assert cast_member.id.version == 4
        assert cast_member.id == valid_id

        assert cast_member.name == valid_name
        assert cast_member.type == valid_type

    def test_creates_cast_member_with_auto_id(self, valid_name, valid_type):
        cast_member = CastMember(name=valid_name, type=valid_type)

        assert isinstance(cast_member.id, UUID)
        assert cast_member.id.version == 4

    def test_raises_error_for_empty_name(self, valid_type):
        with pytest.raises(ValueError, match="name cannot be empty"):
            CastMember(name="", type=valid_type)

    def test_raises_error_for_name_longer_than_255_chars(self, valid_type):
        long_name = "a" * 256
        with pytest.raises(ValueError, match="name cannot be longer than 255"):
            CastMember(name=long_name, type=valid_type)

    def test_raises_error_for_non_uuid_id(self, valid_name, valid_type):
        with pytest.raises(ValueError, match="id must be a UUID instance"):
            CastMember(id="not-a-uuid", name=valid_name, type=valid_type)

    def test_raises_error_for_non_uuidv4_id(self, valid_name, valid_type):
        invalid_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, "example.com")
        assert invalid_uuid.version == 5

        with pytest.raises(ValueError, match="id must be a valid UUIDv4"):
            CastMember(id=invalid_uuid, name=valid_name, type=valid_type)

    def test_raises_error_for_invalid_cast_member_type(self, valid_name):
        with pytest.raises(ValueError, match="type must be a valid CastMemberType"):
            CastMember(name=valid_name, type="invalid-type")


class TestUpdateCastMember:
    def test_update_cast_member_with_valid_data(self, valid_id, valid_cast_member):
        cast_member = valid_cast_member
        new_name = "Zombie"
        new_type = CastMemberType.DIRECTOR
        cast_member.update_cast_member(new_name, new_type)

        assert isinstance(cast_member.id, UUID)
        assert cast_member.id.version == 4
        assert cast_member.id == valid_id

        assert cast_member.name == new_name
        assert cast_member.type == new_type

    def test_update_raises_error_for_empty_name(self, valid_cast_member, valid_type):
        empty_name = ""
        with pytest.raises(ValueError, match="name cannot be empty"):
            valid_cast_member.update_cast_member(name=empty_name, type=valid_type)

    def test_update_raises_error_for_name_longer_than_255_chars(
        self, valid_cast_member, valid_type
    ):
        long_name = "a" * 256
        with pytest.raises(ValueError, match="name cannot be longer than 255"):
            CastMember(name=long_name, type=valid_type)
            valid_cast_member.update_cast_member(name=long_name, type=valid_type)

    def test_update_raises_error_for_invalid_cast_member_type(
        self, valid_cast_member, valid_name
    ):
        with pytest.raises(ValueError, match="type must be a valid CastMemberType"):
            valid_cast_member.update_cast_member(name=valid_name, type="invalid-type")


class TestEquality:
    def test_when_cast_members_have_same_id_they_are_equal(self):
        common_id = uuid.uuid4()

        cast_member1 = CastMember(id=common_id, name="Steve", type=CastMemberType.ACTOR)
        cast_member2 = CastMember(
            id=common_id, name="Zombie", type=CastMemberType.DIRECTOR
        )

        assert cast_member1 == cast_member2

    def test_equality_different_classes(self):
        class Dummy:
            pass

        common_id = uuid.uuid4()
        cast_member = CastMember(id=common_id, name="Steve", type=CastMemberType.ACTOR)
        dummy_cast_member = Dummy()
        dummy_cast_member.id = common_id

        assert cast_member != dummy_cast_member
