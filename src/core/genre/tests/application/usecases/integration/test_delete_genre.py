import uuid

import pytest

from src.core.genre.application.exceptions import GenreNotFound
from src.core.genre.application.usecases.delete_genre import (
    DeleteGenre,
)
from src.core.genre.domain.genre import Genre
from src.core.genre.infra.in_memory_genre_repository import InMemoryGenreRepository


@pytest.fixture
def adventure_genre():
    return Genre(id=uuid.uuid4(), name="Adventure", categories=[uuid.uuid4()])


@pytest.fixture
def genre_repository(adventure_genre):
    repository = InMemoryGenreRepository()
    repository.genres = [adventure_genre]
    return repository


class TestDeleteGenre:
    def test_delete_genre_from_repository(self, genre_repository, adventure_genre):
        initial_count = len(genre_repository.genres)
        use_case = DeleteGenre(repository=genre_repository)
        input = DeleteGenre.Input(id=adventure_genre.id)

        use_case.execute(input=input)

        assert len(genre_repository.genres) == initial_count - 1
        assert all(item.id != adventure_genre.id for item in genre_repository.genres)

    def test_when_genre_not_found_then_raises_exception(self, genre_repository):
        use_case = DeleteGenre(repository=genre_repository)
        fake_id = uuid.uuid4()
        input = DeleteGenre.Input(id=fake_id)

        with pytest.raises(GenreNotFound):
            use_case.execute(input=input)
