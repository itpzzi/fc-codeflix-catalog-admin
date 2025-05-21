from dataclasses import dataclass
from pathlib import Path, PosixPath
from uuid import UUID

from src.core._shared.events.abstract_message_bus import AbstractMessageBus
from src.core._shared.events.message_bus import MessageBus
from src.core._shared.infra.storage.abstract_storage_service import (
    AbstractStorageService,
)
from src.core.video.application.events.integration_events import (
    AudioVideoMediaUpdatedIntegrationEvent,
)
from src.core.video.application.exceptions import (
    CouldNotStoreMedia,
    VideoNotFound,
)
from src.core.video.domain.events.domain_events import AudioVideoMediaUpdatedEvent
from src.core.video.domain.value_objects import AudioVideoMedia, MediaStatus, MediaType
from src.core.video.domain.video import Video
from src.core.video.domain.video_repository import IVideoRepository


class UploadVideo:

    @dataclass
    class Input:
        video_id: UUID
        file_name: str
        content_type: str
        content: bytes

    @dataclass
    class UploadVideoData(Input):
        full_path: PosixPath

    def __init__(
        self,
        repository: IVideoRepository,
        storage: AbstractStorageService,
        message_bus: AbstractMessageBus = None,
    ) -> None:
        self.repository = repository
        self.storage = storage
        self.message_bus = message_bus if message_bus else MessageBus()

    def execute(self, input: Input) -> None:
        video = self._get_video_or_raise(input.video_id)
        video_data = self._build_video_data(input)
        media = self._build_audio_video_media(video_data)
        self._store_file(video_data)
        self._persist_video_changes(video, media)
        self._pull_domain_events_and_convert_to_integration_events(video)

    def _get_video_or_raise(self, video_id: UUID) -> Video:
        video = self.repository.get_by_id(video_id)
        if not video:
            raise VideoNotFound(
                f"Cannot update non-existent video. {video_id} not found"
            )
        return video

    def _build_video_data(self, input: Input) -> UploadVideoData:
        safe_path = Path("videos") / f"{input.video_id}" / f"{input.file_name}"
        return self.UploadVideoData(
            video_id=input.video_id,
            file_name=input.file_name,
            content_type=input.content_type,
            content=input.content,
            full_path=safe_path,
        )

    def _build_audio_video_media(self, data: UploadVideoData) -> AudioVideoMedia:
        return AudioVideoMedia(
            name=data.file_name,
            raw_location=str(data.full_path),
            encoded_location="",
            status=MediaStatus.PENDING,
            media_type=MediaType.VIDEO,
        )

    def _store_file(self, data: UploadVideoData) -> None:
        try:
            self.storage.store(
                file_name=data.full_path,
                content_type=data.content_type,
                content=data.content,
            )
        except Exception as error:
            raise CouldNotStoreMedia(f"Failed to store video file: {str(error)}")

    def _persist_video_changes(self, video: Video, media: AudioVideoMedia) -> None:
        video.update_video(media)
        self.repository.update(video)

    def _pull_domain_events_and_convert_to_integration_events(self, video: Video):
        events = video.pull_events()
        integration_events = []

        for event in events:
            if isinstance(event, AudioVideoMediaUpdatedEvent):
                integration_events.append(
                    AudioVideoMediaUpdatedIntegrationEvent(
                        resource_id=f"{event.aggregate_id}.{event.media_type}",
                        file_path=event.full_path,
                    )
                )

        if len(integration_events) > 0:
            self.message_bus.handle(integration_events)
