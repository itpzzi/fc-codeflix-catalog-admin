from src.core.video.domain.value_objects import MediaStatus, Rating
from src.core.video.domain.video import Video
from src.django_project.video_app.models import Video as VideoModel


def parse_media_status_enum(value: str) -> MediaStatus:
    if "." in value:
        return MediaStatus[value.split(".")[-1]]
    return MediaStatus[value]

def parse_rating_enum(value: str) -> Rating:
    if "." in value:
        return Rating[value.split(".")[-1]]
    return Rating[value]


def get_ids_from_queryset(queryset) -> set[str]:
    return set(queryset.values_list("id", flat=True))


class VideoModelMapper:
    @staticmethod
    def to_entity(model: VideoModel) -> Video:
        return Video(
            id=model.id,
            title=model.title,
            description=model.description,
            duration=model.duration,
            launch_year=model.launch_year,
            rating=parse_rating_enum(model.rating),
            opened=model.opened,
            categories=get_ids_from_queryset(model.categories),
            genres=get_ids_from_queryset(model.genres),
            cast_members=get_ids_from_queryset(model.cast_members),
        )

    @staticmethod
    def to_model(entity: Video) -> VideoModel:
        model = VideoModel(
            id=entity.id,
            title=entity.title,
            description=entity.description,
            duration=entity.duration,
            launch_year=entity.launch_year,
            rating=entity.rating.name,
            opened=entity.opened,
            published=entity.published,
        )
        return model
