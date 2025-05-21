import logging

from src.core._shared.events.event import IntegrationEvent
from src.core._shared.events.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)


class RabitMQDispatcher(EventDispatcher):
    def dispatch(self, event: IntegrationEvent):
        logger.info(f"Dispatching {event.__class__.__name__} to RabbitMQ")
