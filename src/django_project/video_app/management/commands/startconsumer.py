import json
import logging
import os
import time

import pika
from django.core.management.base import BaseCommand
from pika.exceptions import (
    AMQPConnectionError,
    ChannelClosedByBroker,
)

from src.core.video.application.exceptions import (
    MediaNotFound,
    UnsupportedMediaType,
    VideoNotFound,
)
from src.core.video.application.usecases.process_audio_video_media import (
    ProcessAudioVideoMedia,
)
from src.core.video.infra.process_audio_video_media_deserializer import (
    ProcessAudioVideoMediaDeserializer,
    UseCaseInput,
)
from src.django_project.video_app.repository import video_repository

logger = logging.getLogger(__name__)

QUEUE_NAME = "videos.converted"
RABBITMQ_HOST = os.environ.get("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = os.environ.get("RABBITMQ_PORT", "5672")
RETRY_DELAY = 5


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument(
            "--once", action="store_true", help="Run the consumer only once"
        )

    def handle(self, *args, **options):
        once = options.get("once", False)

        while True:
            try:
                connection = self._create_connection()
                channel = self._setup_channel(connection)

                if once:
                    self._process_single_message(channel, connection)
                    return
                else:
                    self._start_continuous_consuming(channel)

            except (AMQPConnectionError, ChannelClosedByBroker) as e:
                self._handle_connection_error(e)
            except KeyboardInterrupt:
                logger.info("Consumer stopped by user")
                break
            except Exception as e:
                logger.critical(f"Unexpected error: {e}. Shutting down.")
                break
            finally:
                self._close_connection_safely(locals().get("connection"))

    def _create_connection(self):
        """Create and return a RabbitMQ connection"""
        self.stdout.write(
            f"Connecting to RabbitMQ at {RABBITMQ_HOST}:{RABBITMQ_PORT}..."
        )
        return pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))

    def _setup_channel(self, connection):
        """Setup and configure the RabbitMQ channel"""
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        return channel

    def _process_single_message(self, channel, connection):
        """Process only one message from the queue"""
        logger.info(f"Waiting for a single message on queue '{QUEUE_NAME}'")

        method, props, body = channel.basic_get(queue=QUEUE_NAME, auto_ack=False)
        if body:
            self._handle_message(channel, method, props, body)
        else:
            logger.info("No messages available in queue")

        connection.close()

    def _start_continuous_consuming(self, channel):
        """Start continuous message consuming"""
        logger.info(f"Starting continuous consumer on queue '{QUEUE_NAME}'")

        channel.basic_consume(
            queue=QUEUE_NAME,
            on_message_callback=self._handle_message,
        )
        channel.start_consuming()

    def _handle_message(self, ch, method, properties, body):
        """Process a single message from RabbitMQ"""
        try:
            self.stdout.write(f"Processing message: {body}")

            payload = json.loads(body)
            deserializer = ProcessAudioVideoMediaDeserializer(
                data=payload, dto_class=UseCaseInput
            )
            deserializer.is_valid(raise_exception=True)
            input = ProcessAudioVideoMedia.Input(**deserializer.validated_data)

            use_case = ProcessAudioVideoMedia(repository=video_repository)
            use_case.execute(input=input)

            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.info(f"Successfully processed video {input.video_id}")

        except (VideoNotFound, UnsupportedMediaType, MediaNotFound, ValueError) as e:
            logger.warning(f"Application error: {e}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Unhandled error: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag)

    def _deserialize_message(self, body):
        """Deserialize RabbitMQ message body into use case input"""

    def _execute_video_processing(self, input_data):
        """Execute the video processing use case"""
        self.stdout.write(f"Processing video with id {input_data.video_id}")

    def _handle_connection_error(self, error):
        """Handle RabbitMQ connection errors with retry logic"""
        logger.error(
            f"Connection failed: {error}. Retrying in {RETRY_DELAY} seconds..."
        )
        time.sleep(RETRY_DELAY)

    def _close_connection_safely(self, connection):
        """Safely close RabbitMQ connection if it exists and is open"""
        if connection and connection.is_open:
            connection.close()
