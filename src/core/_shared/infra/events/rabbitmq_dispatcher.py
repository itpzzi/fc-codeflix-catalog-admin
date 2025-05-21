import json
import logging

import pika

from src.core._shared.events.event import IntegrationEvent
from src.core._shared.events.event_dispatcher import EventDispatcher

logger = logging.getLogger(__name__)


class RabbitMQDispatcher(EventDispatcher):
    def __init__(self, host="localhost", queue_name="videos.new"):
        self.host = host
        self.queue_name = queue_name
        self.connection = None
        self.channel = None
        self.connection_params = None

    def dispatch(self, event: IntegrationEvent):
        self._open_connection_if_needed()
        logger.info(f"Dispatching {event.__class__.__name__} to RabbitMQ")
        payload = self._serialize_event(event)
        self._publish(payload)
        logger.info(f"Dispatched event payload: {payload}")

    def _open_connection_if_needed(self):
        if self.connection is None:
            try:
                connection_params = pika.ConnectionParameters(host=self.host)
                self.connection = pika.BlockingConnection(connection_params)
                self.channel = self.connection.channel()

                self.channel.queue_declare(queue=self.queue_name, durable=True)
                logger.debug(
                    f"Established connection to RabbitMQ and declared queue '{self.queue_name}'"
                )
            except Exception as error:
                logger.error(
                    f"Failed to connect to RabbitMQ: {str(error)}", exc_info=True
                )
                raise

    def _serialize_event(self, event: IntegrationEvent) -> str:
        return json.dumps(event.payload)

    def _publish(self, payload: str):
        try:

            properties = pika.BasicProperties(
                delivery_mode=2,
            )

            self.channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=payload,
                properties=properties,
            )
            logger.info(f"Sent message to queue '{self.queue_name}'")
            logger.debug(f"Message payload: {payload}")
        except Exception as error:
            logger.error(f"Failed to publish message: {str(error)}", exc_info=True)
            raise
