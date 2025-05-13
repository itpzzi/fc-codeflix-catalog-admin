from typing import Set
from uuid import UUID

from src.core.genre.domain.genre import Genre
from src.django_project.genre_app.models import Genre as GenreModel


class GenreModelMapper:
    @staticmethod
    def to_entity(model: GenreModel) -> Genre:
        categories: Set[UUID] = set(model.categories.values_list("id", flat=True))
        return Genre(
            id=model.id,
            name=model.name,
            is_active=model.is_active,
            categories=categories,
        )

    @staticmethod
    def to_model(genre: Genre) -> GenreModel:
        model = GenreModel(
            id=genre.id,
            name=genre.name,
            is_active=genre.is_active,
        )
        model.categories.set(genre.categories)
        return model
