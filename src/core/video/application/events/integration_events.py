from dataclasses import dataclass

from src.core._shared.events.event import IntegrationEvent


@dataclass(frozen=True)
class AudioVideoMediaUpdatedIntegrationEvent(IntegrationEvent):
    resource_id: str
    file_path: str
