from src.core._shared.application.handlers import EventHandler
from src.core._shared.events.event_dispatcher import EventDispatcher
from src.core.video.application.events.integration_events import (
    AudioVideoMediaUpdatedIntegrationEvent,
)


class PublishAudioVideoMediaUpdatedEventHandler(
    EventHandler[AudioVideoMediaUpdatedIntegrationEvent]
):
    def __init__(self, dispatcher: EventDispatcher):
        self.dispatcher = dispatcher

    def handle(self, event: AudioVideoMediaUpdatedIntegrationEvent) -> None:
        self.dispatcher.dispatch(event)
