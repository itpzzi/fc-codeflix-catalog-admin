from dataclasses import dataclass
from uuid import UUID

from src.core.video.application.exceptions import (
    MediaNotFound,
    UnsupportedMediaType,
    VideoNotFound,
)
from src.core.video.domain.value_objects import MediaStatus, MediaType
from src.core.video.domain.video import Video
from src.core.video.domain.video_repository import IVideoRepository


class ProcessAudioVideoMedia:

    @dataclass
    class Input:
        video_id: UUID
        encoded_location: str
        media_status: MediaStatus
        media_type: MediaType

    def __init__(self, repository: IVideoRepository):
        self._repository = repository

    def execute(self, input: Input) -> None:
        print(input)
        video = self._get_video_or_raise(input.video_id)
        if input.media_type == MediaType.VIDEO:
            self._process_video_media(input, video)
        elif input.media_type == MediaType.TRAILER:
            self._process_trailer_media(input)

        self._repository.update(video)

    def _get_video_or_raise(self, video_id: UUID) -> Video:
        video = self._repository.get_by_id(video_id)
        if not video:
            raise VideoNotFound(f"Video with id {video_id} not found")
        return video

    def _process_video_media(self, input: Input, video: Video):
        if not video.video:
            raise MediaNotFound("Video must have a video media to be processed")
        video.process(
            status=input.media_status, encoded_location=input.encoded_location
        )

    def _process_trailer_media(self, input: Input):
        raise UnsupportedMediaType("Trailer media type is currently not supported")
