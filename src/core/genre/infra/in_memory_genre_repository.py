from uuid import UUID

from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import (
    IGenreRepository,
)


class InMemoryGenreRepository(IGenreRepository):
    def __init__(self, genres=None):
        self.genres = genres or []

    def save(self, genre: Genre) -> None:
        self.genres.append(genre)

    def get_by_id(self, id: UUID) -> Genre | None:
        for genre in self.genres:
            if genre.id == id:
                return genre
        return None

    def delete(self, id: UUID) -> None:
        genre_to_delete = self.get_by_id(id)
        if genre_to_delete:
            self.genres.remove(genre_to_delete)

    def update(self, genre: Genre) -> None:
        old_genre = self.get_by_id(genre.id)
        if old_genre:
            self.genres.remove(old_genre)
            self.genres.append(genre)

    def list(self) -> list[Genre]:
        return self.genres.copy()
