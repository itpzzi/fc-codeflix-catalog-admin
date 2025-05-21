from abc import ABC, abstractmethod
from typing import Generic

from src.core._shared.events.event import TEvent


class EventHandler(ABC, Generic[TEvent]):
    @abstractmethod
    def handle(self, event: TEvent) -> None:
        pass
