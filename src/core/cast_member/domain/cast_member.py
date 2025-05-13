from dataclasses import dataclass
from enum import StrEnum
from uuid import UUID

from src.core._shared.entity import Entity


class CastMemberType(StrEnum):
    DIRECTOR = "director"
    ACTOR = "actor"


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

    def _validate_id(self, value: UUID):
        if not isinstance(value, UUID):
            raise ValueError("id must be a UUID instance")
        if value.version != 4:
            raise ValueError("id must be a valid UUIDv4")

    def _validate_name(self, value: str):
        if not value:
            raise ValueError("name cannot be empty")
        if len(value) > 255:
            raise ValueError("name cannot be longer than 255 characters")

    def _validate_type(self, value: CastMemberType):
        if value not in CastMemberType:
            raise ValueError("type must be a valid CastMemberType")

    def __repr__(self):
        return f"<CastMember {self.name} ({self.type}) - {self.id}>"

    def __str__(self):
        return f"{self.name} ({self.type})"
