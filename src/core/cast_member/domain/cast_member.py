from dataclasses import dataclass
from enum import StrEnum

from src.core._shared.entity import Entity


class CastMemberType(StrEnum):
    DIRECTOR = "director"
    ACTOR = "actor"

    @classmethod
    def _missing_(cls, value: object):
        if value not in cls._value2member_map_:
            raise ValueError("type must be a valid CastMemberType")
        return cls._value2member_map_[value]


@dataclass(eq=False)
class CastMember(Entity):
    type: CastMemberType

    def validate(self):
        self._validate_id(self.id)
        self._validate_name(self.name)
        self._validate_type(self.type)

    def update_cast_member(self, name: str, type: CastMemberType):
        self.name = name
        self.type = type

        self.validate()

    def _validate_type(self, value: CastMemberType):
        CastMemberType(value)

    def __repr__(self):
        return f"<CastMember {self.name} ({self.type}) - {self.id}>"

    def __str__(self):
        return f"{self.name} ({self.type})"
