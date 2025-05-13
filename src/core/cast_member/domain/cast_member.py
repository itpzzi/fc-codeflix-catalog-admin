from dataclasses import dataclass, field
from enum import StrEnum
from uuid import UUID, uuid4


class CastMemberType(StrEnum):
    DIRECTOR = "director"
    ACTOR = "actor"


@dataclass
class CastMember:
    name: str
    type: CastMemberType
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self):
        self.validate()

    def update_cast_member(self, name: str, type: CastMemberType):
        self.name = name
        self.type = type

        self.validate()

    def validate(self):
        self._validate_id_is_valid_uuid4(self.id)
        self._validate_name_is_valid(self.name)
        self._validate_type_is_valid(self.type)

    def _validate_id_is_valid_uuid4(self, value: UUID):
        if not isinstance(value, UUID):
            raise ValueError("id must be a UUID instance")
        if value.version != 4:
            raise ValueError("id must be a valid UUIDv4")

    def _validate_name_is_valid(self, value: str):
        if not value:
            raise ValueError("name cannot be empty")
        if len(value) > 255:
            raise ValueError("name cannot be longer than 255 characters")

    def _validate_type_is_valid(self, value: CastMemberType):
        if value not in CastMemberType:
            raise ValueError("type must be a valid CastMemberType")

    def __eq__(self, other) -> bool:
        if not isinstance(other, CastMember):
            return False

        return other.id == self.id

    def __repr__(self):
        return f"<CastMember {self.name} ({self.type}) - {self.id}>"

    def __str__(self):
        return f"{self.name} ({self.type})"
