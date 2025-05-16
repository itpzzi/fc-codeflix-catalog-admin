from uuid import UUID

from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction

from django_project.video_app.mapper import VideoModelMapper
from src.core.video.domain.video import Video
from src.core.video.domain.video_repository import IVideoRepository
from src.django_project.video_app.models import Video as VideoModel


class DjangoORMVideoRepository(IVideoRepository):
    def __init__(self, model: VideoModel = VideoModel):
        self.model = model

    def save(self, entity: Video) -> None:
        with transaction.atomic():
            model = VideoModelMapper.to_model(entity)
            model.save()
            model.categories.set(entity.categories)
            model.genres.set(entity.genres)
            model.cast_members.set(entity.cast_members)

    def get_by_id(self, id: UUID) -> Video | None:
        try:
            model = self.model.objects.get(id=id)
            return VideoModelMapper.to_entity(model)
        except ObjectDoesNotExist:
            return None

    def delete(self, id: UUID) -> None:
        self.model.objects.filter(id=id).delete()

    def update(self, video: Video) -> None:
        with transaction.atomic():
            model = self.model.objects.get(id=video.id)
            model.title = video.title
            model.description = video.description
            model.duration = video.duration
            model.launch_year = video.launch_year
            model.rating = video.rating.name
            model.opened = video.opened
            model.published = video.published
            model.save()
            model.categories.set(video.categories)
            model.genres.set(video.genres)
            model.cast_members.set(video.cast_members)

    def list(self) -> list[Video]:
        models = self.model.objects.all()
        return [VideoModelMapper.to_entity(model) for model in models]
