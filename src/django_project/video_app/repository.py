from uuid import UUID

from django.db import transaction

from src.core.video.domain.video import Video
from src.core.video.domain.video_repository import IVideoRepository
from src.django_project.video_app.mapper import VideoModelMapper
from src.django_project.video_app.models import (
    AudioVideoMedia as AudioVideoMediaModel,
)
from src.django_project.video_app.models import (
    Video as VideoModel,
)


class DjangoORMVideoRepository(IVideoRepository):
    def __init__(self, model: VideoModel = VideoModel):
        self.model = model

    def save(self, video: Video) -> None:
        with transaction.atomic():
            model = VideoModelMapper.to_model(video)
            model.save()
            model.categories.set(video.categories)
            model.genres.set(video.genres)
            model.cast_members.set(video.cast_members)

    def get_by_id(self, id: UUID) -> Video | None:
        try:
            model = self.model.objects.get(id=id)
            return VideoModelMapper.to_entity(model)
        except self.model.DoesNotExist:
            return None

    def delete(self, id: UUID) -> None:
        self.model.objects.filter(id=id).delete()

    def update(self, video: Video) -> None:
        try:
            video_model = self.model.objects.get(id=video.id)
        except self.model.DoesNotExist:
            return None
        else:
            AudioVideoMediaModel.objects.filter(id=video.id).delete()

            video_model.categories.set(video.categories)
            video_model.genres.set(video.genres)
            video_model.cast_members.set(video.cast_members)

            video_model.video = AudioVideoMediaModel.objects.create(
                name=video.video.name,
                raw_location=video.video.raw_location,
                encoded_location=video.video.encoded_location,
                status=video.video.status,
                media_type=video.video.media_type,
            )

            video_model.title = video.title
            video_model.description = video.description
            video_model.duration = video.duration
            video_model.launch_year = video.launch_year
            video_model.rating = video.rating.name
            video_model.opened = video.opened
            video_model.published = video.published

            video_model.save()

    def list(self) -> list[Video]:
        models = self.model.objects.all()
        return [VideoModelMapper.to_entity(model) for model in models]


video_repository = DjangoORMVideoRepository()
