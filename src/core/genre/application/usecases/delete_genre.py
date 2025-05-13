from dataclasses import dataclass
from uuid import UUID

from src.core.genre.application.exceptions import GenreNotFound
from src.core.genre.domain.genre_repository import IGenreRepository


@dataclass
class DeleteGenreInput:
    id: UUID


@dataclass
class DeleteGenreOutput:
    pass


class DeleteGenreUseCase:

    def __init__(self, repository: IGenreRepository):
        self.repository = repository

    def execute(self, input: DeleteGenreInput) -> None:
        genre_from_repo = self.repository.get_by_id(input.id)

        if not genre_from_repo:
            raise GenreNotFound(
                f"Cannot delete non-existent genre. {input.id} not found"
            )

        self.repository.delete(genre_from_repo.id)
