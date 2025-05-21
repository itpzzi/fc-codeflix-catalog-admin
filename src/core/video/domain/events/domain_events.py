"""
AudioVideoMediaUpdatedEvent(
    aggregate_id=self.id,
    full_path=value.raw_location,
    media_type=MediaType.VIDEO,
)
"""

from dataclasses import dataclass
from uuid import UUID

from src.core._shared.events.event import DomainEvent
from src.core.video.domain.value_objects import MediaType


@dataclass(frozen=True)
class AudioVideoMediaUpdatedEvent(DomainEvent):
    aggregate_id: UUID
    full_path: str
    media_type: MediaType
