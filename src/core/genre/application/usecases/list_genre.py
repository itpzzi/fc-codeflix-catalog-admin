from dataclasses import dataclass
from uuid import UUID

from src.core._shared.application.list_entity import ListEntityInput, ListEntityOutput
from src.core.genre.domain.genre_repository import IGenreRepository


@dataclass
class ListGenreItem:
    name: str
    id: UUID
    categories: set[UUID]
    is_active: bool


class ListGenre:
    Input = ListEntityInput
    Output = ListEntityOutput[ListGenreItem]

    def __init__(self, repository: IGenreRepository):
        self.repository = repository

    def execute(self, input: Input) -> Output:
        genres = self.repository.list()
        genre_items = [
            ListGenreItem(
                name=g.name, id=g.id, categories=g.categories, is_active=g.is_active
            )
            for g in genres
        ]
        return self.Output(input, genre_items)
