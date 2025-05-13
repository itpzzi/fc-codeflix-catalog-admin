from uuid import UUID

from django.db import transaction

from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import IGenreRepository
from src.django_project.genre_app.models import Genre as GenreModel


def get_category_ids(genre_model):
    return set(genre_model.categories.values_list("id", flat=True))


class DjangoORMGenreRepository(IGenreRepository):
    def __init__(self, model: GenreModel = GenreModel):
        self.model = model

    def save(self, genre: Genre) -> None:
        with transaction.atomic():
            genre_model = self.model.objects.create(
                id=genre.id,
                name=genre.name,
                is_active=genre.is_active,
            )
            genre_model.categories.set(genre.categories)

    def get_by_id(self, id: UUID) -> Genre | None:
        try:
            genre_model = self.model.objects.get(pk=id)

            only_categories_ids = get_category_ids(genre_model=genre_model)

            return Genre(
                id=genre_model.id,
                name=genre_model.name,
                is_active=genre_model.is_active,
                categories=only_categories_ids,
            )
        except self.model.DoesNotExist:
            return None

    def delete(self, id: UUID) -> None:
        self.model.objects.filter(id=id).delete()

    def update(self, genre: Genre) -> None:
        try:
            genre_model = self.model.objects.get(pk=genre.id)
        except self.model.DoesNotExist:
            return None

        with transaction.atomic():
            self.model.objects.filter(pk=genre.id).update(
                name=genre.name,
                is_active=genre.is_active,
            )
            genre_model.categories.set(genre.categories)

    def list(self) -> list[Genre]:
        return [
            Genre(
                id=genre_model.id,
                name=genre_model.name,
                categories=get_category_ids(genre_model),
                is_active=genre_model.is_active,
            )
            for genre_model in self.model.objects.all()
        ]
