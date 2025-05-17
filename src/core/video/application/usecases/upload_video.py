from dataclasses import dataclass
from pathlib import Path, PosixPath
from uuid import UUID

from src.core._shared.infra.storage.abstract_storage_service import (
    AbstractStorageService,
)
from src.core.video.application.exceptions import VideoNotFound
from src.core.video.domain.value_objects import AudioVideoMedia, MediaStatus
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
        self, repository: IVideoRepository, storage: AbstractStorageService
    ) -> None:
        self.repository = repository
        self.storage = storage

    def execute(self, input: Input) -> None:
        video = self._get_video_or_raise(input.video_id)
        video_data = self._build_video_data(input)
        media = self._build_audio_video_media(video_data)
        self._store_file(video_data)
        self._persist_video_changes(video, media)

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
        )

    def _store_file(self, data: UploadVideoData) -> None:
        self.storage.store(
            file_name=data.full_path,
            content_type=data.content_type,
            content=data.content,
        )

    def _persist_video_changes(self, video: Video, media: AudioVideoMedia) -> None:
        video.update_video(media)
        self.repository.update(video)
