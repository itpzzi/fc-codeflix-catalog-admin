from dataclasses import dataclass
from decimal import Decimal
from enum import Enum, auto, unique
from typing import Union
from uuid import UUID

from src.core._shared.common_types import Location, Name


class Title(str):
    def __new__(cls, value: str):
        if not value:
            raise ValueError("title cannot be empty")
        if len(value) > 255:
            raise ValueError("title cannot be longer than 255 characters")
        return super().__new__(cls, value)


class Description(str):
    def __new__(cls, value: str):
        if not value:
            raise ValueError("description cannot be empty")
        if len(value) > 1000:
            raise ValueError("description cannot be longer than 1000 characters")
        return super().__new__(cls, value)


class Duration(Decimal):
    def __new__(cls, value: Union[int, float, str, Decimal]):
        try:
            decimal_value = Decimal(str(value))
        except Exception:
            raise TypeError("duration must be a number or numeric string")

        if decimal_value <= 0:
            raise ValueError("duration must be a positive number")
        if decimal_value > Decimal("1000"):
            raise ValueError("duration is unrealistically long")

        return super().__new__(cls, decimal_value)


class LaunchYear(int):
    def __new__(cls, value: int):
        if not isinstance(value, int):
            raise TypeError("launch year must be a integer number")
        if value < 1900 or value > 2100:
            raise ValueError("launch year must be between 1900 and 2100")
        return super().__new__(cls, value)


class SetUUID(set[UUID]):
    def __new__(cls, value=None):
        if not isinstance(value, set):
            raise TypeError(f"{cls.__name__} must be a set")
        if not all(isinstance(item, UUID) for item in value):
            raise TypeError(f"all items in {cls.__name__} must be UUIDs")
        return super().__new__(cls, value)


class Categories(SetUUID):
    pass


class Genres(SetUUID):
    pass


class CastMembers(SetUUID):
    pass


@unique
class Rating(Enum):
    ER = auto()
    L = auto()
    AGE_10 = auto()
    AGE_12 = auto()
    AGE_14 = auto()
    AGE_16 = auto()
    AGE_18 = auto()


@unique
class MediaStatus(Enum):
    PENDING = auto()
    PROCESSING = auto()
    COMPLETED = auto()
    ERROR = auto()


class MediaType(Enum):
    VIDEO = "VIDEO"
    TRAILER = "TRAILER"


@dataclass(frozen=True)
class ImageMedia:
    name: Name
    location: Location


@dataclass(frozen=True)
class AudioVideoMedia:
    name: Name
    raw_location: Location
    encoded_location: Location
    status: MediaStatus
    media_type: MediaType
