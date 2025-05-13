from unittest.mock import create_autospec
import pytest
import uuid
from src.core.genre.domain.genre_repository import IGenreRepository
from src.core.genre.application.usecases.delete_genre import (
    DeleteGenre,
    DeleteGenreInput,
)
from src.core.genre.application.exceptions import GenreNotFound
from src.core.genre.infra.in_memory_genre_repository import InMemoryGenreRepository
from src.core.genre.domain.genre import Genre


@pytest.fixture
def adventure_genre():
    return Genre(id=uuid.uuid4(), name="Adventure", categories=[uuid.uuid4()])


@pytest.fixture
def mock_genre_repository():
    repository = create_autospec(IGenreRepository)
    return repository


class TestDeleteGenre:
    def test_delete_genre_from_repository(self, mock_genre_repository, adventure_genre):
        use_case = DeleteGenre(repository=mock_genre_repository)
        input = DeleteGenreInput(id=adventure_genre.id)
        mock_genre_repository.get_by_id.return_value = adventure_genre

        use_case.execute(input=input)

        mock_genre_repository.delete.assert_called_once_with(adventure_genre.id)

    def test_when_genre_not_found_then_raises_exception(self, mock_genre_repository):
        use_case = DeleteGenre(repository=mock_genre_repository)
        fake_id = uuid.uuid4()
        input = DeleteGenreInput(id=fake_id)
        mock_genre_repository.get_by_id.return_value = None

        with pytest.raises(
            GenreNotFound,
            match=f"Cannot delete non-existent genre. {input.id} not found",
        ):
            use_case.execute(input=input)

        mock_genre_repository.delete.assert_not_called()
        assert mock_genre_repository.delete.called is False
