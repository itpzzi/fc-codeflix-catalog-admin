from abc import ABC, abstractmethod
from dataclasses import dataclass

from src.core._shared.events.event import Event


@dataclass(frozen=True)
class AbstractMessageBus(ABC):

    @abstractmethod
    def handle(self, events: list[Event]) -> None:
        pass
