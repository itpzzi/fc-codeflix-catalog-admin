from dataclasses import dataclass
from uuid import UUID

from src.core.genre.application.exceptions import GenreNotFound
from src.core.genre.domain.genre_repository import IGenreRepository


@dataclass
class DeleteGenreRequest:
    id: UUID


@dataclass
class DeleteGenreResponse:
    pass


class DeleteGenreUseCase:

    def __init__(self, repository: IGenreRepository):
        self.repository = repository

    def execute(self, request: DeleteGenreRequest) -> None:
        genre_from_repo = self.repository.get_by_id(request.id)

        if not genre_from_repo:
            raise GenreNotFound(
                f"Cannot deleted non-existent genre. {request.id} not found"
            )

        self.repository.delete(genre_from_repo.id)
