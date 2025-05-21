import logging
from typing import Dict, List, Type

from src.core._shared.application.handlers import EventHandler
from src.core._shared.events.abstract_message_bus import AbstractMessageBus
from src.core._shared.events.event import Event, TEvent

logger = logging.getLogger(__name__)


class MessageBus(AbstractMessageBus):
    handlers: Dict[Type[TEvent], List[EventHandler[TEvent]]]

    def __init__(self) -> None:
        self.handlers = {}

    def handle(self, events: List[Event]) -> None:
        for event in events:
            event_type = type(event)
            if event_type not in self.handlers:
                continue
            for handler in self.handlers[event_type]:
                try:
                    handler.handle(event)
                except Exception as e:
                    logger.exception(f"Error handling {event_type.__name__}: {e}")
                    continue

    def register_handler(
        self, event_type: Type[TEvent], handler: EventHandler[TEvent]
    ) -> None:
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        if handler not in self.handlers[event_type]:
            self.handlers[event_type].append(handler)

    def unregister_handler(
        self, event_type: Type[TEvent], handler: EventHandler[TEvent]
    ) -> None:
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            if not self.handlers[event_type]:
                del self.handlers[event_type]
