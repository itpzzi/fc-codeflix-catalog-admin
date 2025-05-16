import pytest
from decimal import Decimal
from uuid import uuid4

from src.core._shared.common_types import CheckSum, Location
from src.core.video.domain.value_objects import (
    CastMembers,
    Categories,
    Description,
    Duration,
    Genres,
    LaunchYear,
    SetUUID,
    Title,
)


# Fixtures
@pytest.fixture
def valid_uuids():
    return {uuid4(), uuid4()}


@pytest.fixture
def valid_duration_values():
    return [120, 120.5, "85.75", Decimal("99.99")]


# Tests de objetos inválidos
class TestInvalidTitle:
    def test_empty(self):
        with pytest.raises(ValueError, match="title cannot be empty"):
            Title("")

    def test_too_long(self):
        with pytest.raises(ValueError, match="title cannot be longer than 255 characters"):
            Title("a" * 256)


class TestInvalidDescription:
    def test_empty(self):
        with pytest.raises(ValueError, match="description cannot be empty"):
            Description("")

    def test_too_long(self):
        with pytest.raises(ValueError, match="description cannot be longer than 1000 characters"):
            Description("a" * 1001)


class TestInvalidDuration:
    def test_negative(self):
        with pytest.raises(ValueError, match="duration must be a positive number"):
            Duration(-5.0)

    def test_too_high(self):
        with pytest.raises(ValueError, match="duration is unrealistically long"):
            Duration(1001.0)

    def test_zero(self):
        with pytest.raises(ValueError, match="duration must be a positive number"):
            Duration(0)

    def test_non_numeric_string(self):
        with pytest.raises(TypeError, match="duration must be a number or numeric string"):
            Duration("invalid")

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="duration must be a number or numeric string"):
            Duration(object())


class TestInvalidLaunchYear:
    def test_low(self):
        with pytest.raises(ValueError, match="launch year must be between 1900 and 2100"):
            LaunchYear(1800)

    def test_high(self):
        with pytest.raises(ValueError, match="launch year must be between 1900 and 2100"):
            LaunchYear(2200)


class TestInvalidCheckSum:
    def test_empty(self):
        with pytest.raises(ValueError, match="checksum cannot be empty"):
            CheckSum("")

    def test_too_short(self):
        with pytest.raises(ValueError, match="checksum must be between 32 and 64 characters"):
            CheckSum("a" * 31)

    def test_too_long(self):
        with pytest.raises(ValueError, match="checksum must be between 32 and 64 characters"):
            CheckSum("a" * 65)


class TestInvalidLocation:
    def test_empty(self):
        with pytest.raises(ValueError, match="location cannot be empty"):
            Location("")

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="location must be a valid path or URL"):
            Location("ftp://invalid")


class TestInvalidSetUUID:
    @pytest.mark.parametrize(
        "cls,invalid_input,expected_message",
        [
            (SetUUID, ["not", "a", "set"], "SetUUID must be a set"),
            (Categories, ["string"], "Categories must be a set"),
            (Genres, {123}, "all items in Genres must be UUIDs"),
            (CastMembers, {None}, "all items in CastMembers must be UUIDs"),
        ],
    )
    def test_invalid_inputs(self, cls, invalid_input, expected_message):
        with pytest.raises(TypeError, match=expected_message):
            cls(invalid_input)


# Testes válidos
class TestValidTitle:
    def test_valid(self):
        assert Title("A valid title")


class TestValidDescription:
    def test_valid(self):
        assert Description("A valid description")


class TestValidDuration:
    def test_valid_values(self, valid_duration_values):
        for value in valid_duration_values:
            d = Duration(value)
            assert isinstance(d, Decimal)

    def test_decimal_equivalence(self):
        d = Duration(120.0)
        assert d == Decimal("120")


class TestValidLaunchYear:
    def test_valid(self):
        assert LaunchYear(2020)


class TestValidChecksum:
    def test_min_length(self):
        assert CheckSum("a" * 32)

    def test_max_length(self):
        assert CheckSum("a" * 64)


class TestValidLocation:
    def test_http(self):
        assert Location("http://example.com/video.mp4")

    def test_path(self):
        assert Location("/media/video.mp4")


class TestValidSetUUID:
    def test_setuuid(self, valid_uuids):
        s = SetUUID(valid_uuids)
        assert isinstance(s, set)
        assert s == valid_uuids

    def test_categories(self, valid_uuids):
        c = Categories(valid_uuids)
        assert isinstance(c, Categories)
        assert c == valid_uuids

    def test_genres(self, valid_uuids):
        g = Genres(valid_uuids)
        assert isinstance(g, Genres)
        assert g == valid_uuids

    def test_cast_members(self, valid_uuids):
        cm = CastMembers(valid_uuids)
        assert isinstance(cm, CastMembers)
        assert cm == valid_uuids
