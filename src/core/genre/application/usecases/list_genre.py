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
class ListGenreRequest:
    pass


@dataclass
class ListGenreResponse:
    data: list[GenreOutput]


class ListGenreUseCase:

    def __init__(self, repository: IGenreRepository):
        self.repository = repository

    def execute(self, request: ListGenreRequest) -> ListGenreResponse:
        genres = self.repository.list()

        return ListGenreResponse(
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
