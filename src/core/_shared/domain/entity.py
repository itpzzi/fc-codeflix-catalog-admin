from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.core._shared.common_types import Name
from src.core._shared.events.abstract_message_bus import AbstractMessageBus
from src.core._shared.events.event import DomainEvent
from src.core._shared.events.message_bus import MessageBus
from src.core._shared.notification import Notification


@dataclass(kw_only=True, slots=True)
class Entity(ABC):
    id: UUID = field(default_factory=uuid4)
    notification: Notification = field(default_factory=Notification, init=False)
    events: list[DomainEvent] = field(default_factory=list, init=False)
    message_bus: AbstractMessageBus = field(default_factory=MessageBus, init=True)

    def dispatch(self, event: DomainEvent) -> None:
        self.events.append(event)
        self.message_bus.handle(self.events)

    def __eq__(self, other) -> bool:
        if not isinstance(other, self.__class__):
            return False

        return other.id == self.id

    def __post_init__(self):
        self.validate()
        self._check_notification_has_errors()

    def _check_notification_has_errors(self) -> None:
        if self.notification.has_errors:
            raise ValueError(self.notification.messages)

    @abstractmethod
    def validate(self):
        pass

    def _validate_id(self, value: UUID):
        if not isinstance(value, UUID):
            self.notification.add_error("id must be a UUID instance")
        elif value.version != 4:
            self.notification.add_error("id must be a valid UUIDv4")

    def pull_events(self) -> list[DomainEvent]:
        events = self.events.copy()
        self.events.clear()
        return events


@dataclass(kw_only=True, eq=False)
class EntityNamed(Entity):
    name: Name

    def validate(self):
        self._validate_name(self.name)
        super().validate()

    def _validate_name(self, value: str):
        try:
            Name(value)
        except ValueError as e:
            self.notification.add_error(str(e))
