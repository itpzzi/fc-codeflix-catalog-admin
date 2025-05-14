from uuid import UUID

from django.db import transaction

from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import IGenreRepository
from src.django_project.genre_app.mapper import GenreModelMapper
from src.django_project.genre_app.models import Genre as GenreModel


class DjangoORMGenreRepository(IGenreRepository):
    def __init__(self, model: GenreModel = GenreModel):
        self.model = model

    def save(self, genre: Genre) -> None:
        with transaction.atomic():
            model = GenreModelMapper.to_model(genre)
            model = self.model.objects.create(
                id=model.id,
                name=model.name,
                is_active=model.is_active,
            )
            model.categories.set(genre.categories)

    def get_by_id(self, id: UUID) -> Genre | None:
        try:
            model = self.model.objects.get(pk=id)
            return GenreModelMapper.to_entity(model)
        except self.model.DoesNotExist:
            return None

    def delete(self, id: UUID) -> None:
        self.model.objects.filter(id=id).delete()

    def update(self, genre: Genre) -> None:
        try:
            model = self.model.objects.get(pk=genre.id)
        except self.model.DoesNotExist:
            return None

        with transaction.atomic():
            self.model.objects.filter(pk=genre.id).update(
                name=genre.name,
                is_active=genre.is_active,
            )
            model.categories.set(genre.categories)

    def list(self) -> list[Genre]:
        return [GenreModelMapper.to_entity(model) for model in self.model.objects.all()]
