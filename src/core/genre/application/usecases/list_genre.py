from dataclasses import dataclass
from uuid import UUID

from src.core.genre.domain.genre_repository import IGenreRepository


@dataclass
class ListGenreItem:
    name: str
    id: UUID
    categories: set[UUID]
    is_active: bool


class ListGenre:

    @dataclass
    class Input:
        pass

    @dataclass
    class Output:
        data: list[ListGenreItem]

    def __init__(self, repository: IGenreRepository):
        self.repository = repository

    def execute(self, input: Input) -> Output:
        genres = self.repository.list()

        return self.Output(
            data=[
                ListGenreItem(
                    id=genre.id,
                    name=genre.name,
                    categories=genre.categories,
                    is_active=genre.is_active,
                )
                for genre in genres
            ]
        )
