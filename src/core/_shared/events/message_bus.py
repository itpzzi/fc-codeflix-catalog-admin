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
        logger.debug("Initialized MessageBus with empty handlers dictionary")

    def handle(self, events: List[Event]) -> None:
        logger.debug(f"Processing {len(events)} events")

        for event in events:
            event_type = type(event)
            logger.debug(f"Handling event of type: {event_type.__name__}")

            handlers = self.handlers.get(event_type, [])

            if not handlers:
                logger.warning(
                    f"No handlers registered for event type: {event_type.__name__}"
                )
                continue

            logger.debug(f"Found {len(handlers)} handlers for {event_type.__name__}")

            for handler in handlers:
                try:
                    logger.info(
                        f"Executing handler {handler.__class__.__name__} for event {event.__class__.__name__}"
                    )
                    handler.handle(event)
                except Exception as error:
                    logger.error(
                        f"Error handling {event.__class__.__name__} via {handler.__class__.__name__}: {error}",
                        exc_info=True,
                    )

    def register_handler(
        self, event_type: Type[TEvent], handler: EventHandler[TEvent]
    ) -> None:
        logger.debug(
            f"Registering handler {handler.__class__.__name__} for event type {event_type.__name__}"
        )

        if event_type not in self.handlers:
            self.handlers[event_type] = []
            logger.debug(
                f"Created new handler list for event type {event_type.__name__}"
            )

        if handler not in self.handlers[event_type]:
            self.handlers[event_type].append(handler)
            logger.info(
                f"Added handler {handler.__class__.__name__} for event type {event_type.__name__}"
            )
        else:
            logger.debug(
                f"Handler {handler.__class__.__name__} already registered for {event_type.__name__}"
            )

        logger.debug(
            f"Current registered event types: {[k.__name__ for k in self.handlers.keys()]}"
        )

    def unregister_handler(
        self, event_type: Type[TEvent], handler: EventHandler[TEvent]
    ) -> None:
        if event_type in self.handlers and handler in self.handlers[event_type]:
            self.handlers[event_type].remove(handler)
            logger.info(
                f"Removed handler {handler.__class__.__name__} from {event_type.__name__}"
            )

            if not self.handlers[event_type]:
                del self.handlers[event_type]
                logger.debug(f"Deleted empty handler list for {event_type.__name__}")
        else:
            logger.debug(
                f"Handler {handler.__class__.__name__} not found for {event_type.__name__}"
            )
