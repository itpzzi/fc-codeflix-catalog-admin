from dataclasses import dataclass
from uuid import UUID

from src.core.genre.domain.genre_repository import IGenreRepository


@dataclass
class GenreOutput:
    name: str
    id: UUID
    categories: set[UUID]
    is_active: bool


@dataclass
class ListGenreInput:
    pass


@dataclass
class ListGenreOutput:
    data: list[GenreOutput]


class ListGenre:

    def __init__(self, repository: IGenreRepository):
        self.repository = repository

    def execute(self, input: ListGenreInput) -> ListGenreOutput:
        genres = self.repository.list()

        return ListGenreOutput(
            data=[
                GenreOutput(
                    id=genre.id,
                    name=genre.name,
                    categories=genre.categories,
                    is_active=genre.is_active,
                )
                for genre in genres
            ]
        )
