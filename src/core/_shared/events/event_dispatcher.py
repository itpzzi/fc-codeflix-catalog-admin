from abc import ABC, abstractmethod

from src.core._shared.events.event import TEvent


class EventDispatcher(ABC):
    @abstractmethod
    def dispatch(self, event: TEvent):
        pass
