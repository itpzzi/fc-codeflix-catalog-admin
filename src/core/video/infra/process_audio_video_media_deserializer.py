import re
from uuid import UUID

from src.core._shared.common_types import Location
from src.core._shared.infra.serialization.deserializer import Deserializer
from src.core.video.application.usecases.process_audio_video_media import (
    ProcessAudioVideoMedia,
)
from src.core.video.domain.value_objects import MediaStatus, MediaType

UseCaseInput = ProcessAudioVideoMedia.Input

"""
Expected message format:
{
    "error": "",
    "status": "COMPLETED|ERROR",
    "video": {
        "resource_id": "<uuid-string>.VIDEO|TRAILER",
        "encoded_video_folder": "/path/to/encoded/video"
    }
}
"""


class ProcessAudioVideoMediaDeserializer(Deserializer[UseCaseInput]):
    def to_internal(self) -> dict:
        return {
            "media_status": self._parse_status(),
            "video_id": self._parse_video_id(),
            "encoded_location": self._parse_encoded_location(),
            "media_type": self._parse_media_type(),
        }

    def _parse_status(self) -> MediaStatus:
        status = self.data.get("status")
        error = self.data.get("error")
        if status == "COMPLETED" and not error:
            return MediaStatus.COMPLETED
        return MediaStatus.ERROR

    def _parse_video_id(self) -> UUID:
        raw_id = self.data.get("video", {}).get("resource_id")
        cleaned_id = re.sub(r"\.(VIDEO|TRAILER)$", "", raw_id)
        return UUID(cleaned_id)

    def _parse_encoded_location(self) -> Location:
        path = self.data.get("video", {}).get("encoded_video_folder")
        return Location(path)

    def _parse_media_type(self) -> MediaType:
        media_type = self.data.get("media_type", "VIDEO")
        if media_type == "VIDEO":
            return MediaType.VIDEO
        if media_type == "TRAILER":
            return MediaType.TRAILER
        raise ValueError(f"Invalid media_type: {media_type}")
