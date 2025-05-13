from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.core._shared.notification import Notification


@dataclass(kw_only=True)
class Entity(ABC):
    id: UUID = field(default_factory=uuid4)
    notification: Notification = field(default_factory=Notification)
    name: str

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return other.id == self.id

    def __post_init__(self):
        self.validate()

    @abstractmethod
    def validate(self):
        pass
