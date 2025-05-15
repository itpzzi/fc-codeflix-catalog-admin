from uuid import uuid4

import pytest

from src.core._shared.common_types import CheckSum, Location
from src.core.video.domain.value_objects import (
    CastMembers,
    Categories,
    Description,
    Duration,
    Genres,
    LaunchedAt,
    SetUUID,
    Title,
)


class TestInvalidVideoValueObjects:
    def test_invalid_title_empty(self):
        with pytest.raises(ValueError, match="title cannot be empty"):
            Title("")

    def test_invalid_title_too_long(self):
        with pytest.raises(
            ValueError, match="title cannot be longer than 255 characters"
        ):
            Title("a" * 256)

    def test_invalid_description_empty(self):
        with pytest.raises(ValueError, match="description cannot be empty"):
            Description("")

    def test_invalid_description_too_long(self):
        with pytest.raises(
            ValueError, match="description cannot be longer than 1000 characters"
        ):
            Description("a" * 1001)

    def test_invalid_duration_negative(self):
        with pytest.raises(ValueError, match="duration must be a positive number"):
            Duration(-5.0)

    def test_invalid_duration_too_high(self):
        with pytest.raises(ValueError, match="duration is unrealistically long"):
            Duration(1001.0)

    def test_invalid_launched_at_low(self):
        with pytest.raises(
            ValueError, match="launched year must be between 1900 and 2100"
        ):
            LaunchedAt(1800)

    def test_invalid_launched_at_high(self):
        with pytest.raises(
            ValueError, match="launched year must be between 1900 and 2100"
        ):
            LaunchedAt(2200)

    def test_invalid_checksum_empty(self):
        with pytest.raises(ValueError, match="checksum cannot be empty"):
            CheckSum("")

    def test_invalid_checksum_too_short(self):
        with pytest.raises(
            ValueError, match="checksum must be between 32 and 64 characters"
        ):
            CheckSum("a" * 31)

    def test_invalid_checksum_too_long(self):
        with pytest.raises(
            ValueError, match="checksum must be between 32 and 64 characters"
        ):
            CheckSum("a" * 65)

    def test_invalid_location_empty(self):
        with pytest.raises(ValueError, match="location cannot be empty"):
            Location("")

    def test_invalid_location_format(self):
        with pytest.raises(ValueError, match="location must be a valid path or URL"):
            Location("ftp://invalid")

    @pytest.mark.parametrize(
        "cls,invalid_input,expected_message",
        [
            (SetUUID, ["not", "a", "set"], "SetUUID must be a set"),
            (Categories, ["string"], "Categories must be a set"),
            (Genres, {123}, "all items in Genres must be UUIDs"),
            (CastMembers, {None}, "all items in CastMembers must be UUIDs"),
        ],
    )
    def test_setuuid_invalid_inputs_raise_type_error(
        self, cls, invalid_input, expected_message
    ):
        with pytest.raises(TypeError, match=expected_message):
            cls(invalid_input)


class TestValidVideoValueObjects:
    def test_valid_title(self):
        assert Title("A valid title")

    def test_valid_description(self):
        assert Description("A valid description")

    def test_valid_duration(self):
        assert Duration(120.5)

    def test_valid_launched_at(self):
        assert LaunchedAt(2020)

    def test_valid_checksum_min_length(self):
        assert CheckSum("a" * 32)

    def test_valid_checksum_max_length(self):
        assert CheckSum("a" * 64)

    def test_valid_location_http(self):
        assert Location("http://example.com/video.mp4")

    def test_valid_location_path(self):
        assert Location("/media/video.mp4")

    def test_setuuid_accepts_set_of_uuids(self):
        items = {uuid4(), uuid4()}
        instance = SetUUID(items)
        assert isinstance(instance, set)
        assert instance == items

    def test_categories_accepts_valid_uuids(self):
        ids = {uuid4(), uuid4()}
        categories = Categories(ids)
        assert isinstance(categories, Categories)
        assert categories == ids

    def test_genres_accepts_valid_uuids(self):
        ids = {uuid4()}
        genres = Genres(ids)
        assert isinstance(genres, Genres)
        assert genres == ids

    def test_cast_members_accepts_valid_uuids(self):
        ids = {uuid4(), uuid4(), uuid4()}
        cast_members = CastMembers(ids)
        assert isinstance(cast_members, CastMembers)
        assert cast_members == ids
