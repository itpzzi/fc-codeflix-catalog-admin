import uuid

import pytest

from src.core.genre.domain.genre import Genre
from src.core.genre.domain.genre_repository import IGenreRepository
from src.core.genre.infra.in_memory_genre_repository import (
    InMemoryGenreRepository,
)

# -------------------- Fixtures -------------------- #


@pytest.fixture
def genre_repository() -> IGenreRepository:
    return InMemoryGenreRepository()


@pytest.fixture
def movie_category() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def documentary_category() -> uuid.UUID:
    return uuid.uuid4()


@pytest.fixture
def set_categories(movie_category, documentary_category) -> set[uuid.UUID]:
    return {movie_category, documentary_category}


# -------------------- Testes de criação -------------------- #


class TestCreateGenre:
    def test_can_save_genre(self, genre_repository, set_categories):
        genre = Genre(
            name="Adventure",
            categories=set_categories,
        )

        genre_repository.save(genre)
        saved_genres = genre_repository.list()
        assert len(saved_genres) == 1
        assert saved_genres[0] == genre


# -------------------- Testes de obtenção -------------------- #


class TestGetGenre:
    def test_can_get_by_id(self, genre_repository, set_categories):
        genre_adventure = Genre(
            name="Adventure",
            categories=set_categories,
        )
        genre_action = Genre(
            name="Action",
            categories=set_categories,
        )

        genre_repository.save(genre_adventure)
        genre_repository.save(genre_action)

        searched_genre = genre_repository.get_by_id(genre_action.id)

        assert searched_genre is not None
        assert searched_genre.name == "Action"
        assert searched_genre.is_active is True
        assert searched_genre.categories == set_categories

    def test_return_none_for_non_existent_id(self, genre_repository):
        fake_id = uuid.uuid4()

        response = genre_repository.get_by_id(fake_id)

        assert response is None


# -------------------- Testes de remoção -------------------- #


class TestDeleteGenre:
    def test_can_delete_genre(self, genre_repository, set_categories):
        genre_adventure = Genre(
            name="Adventure",
            categories=set_categories,
        )
        genre_action = Genre(
            name="Action",
            categories=set_categories,
        )

        genre_repository.save(genre_adventure)
        genre_repository.save(genre_action)

        genre_repository.delete(genre_adventure.id)

        assert len(genre_repository.list()) == 1
        assert genre_repository.list()[0].id == genre_action.id


# -------------------- Testes de atualização -------------------- #


class TestUpdateGenre:
    def test_can_update_genre(self, genre_repository, set_categories):
        genre = Genre(
            name="Adventure",
            categories=set_categories,
        )
        genre_repository.save(genre)

        updated = Genre(
            id=genre.id,
            name="Updated Adventure",
            categories=set_categories,
            is_active=False,
        )

        genre_repository.update(updated)

        result = genre_repository.get_by_id(genre.id)
        assert result.name == "Updated Adventure"
        assert result.categories == set_categories
        assert result.is_active is False

    def test_update_nonexistent_genre_does_nothing(
        self, genre_repository, set_categories
    ):
        new_genre = Genre(
            id=uuid.uuid4(),
            name="Documentário",
            categories=set_categories,
        )

        genre_repository.update(new_genre)

        assert genre_repository.get_by_id(new_genre.id) is None

    def test_update_preserves_id(self, genre_repository, set_categories):
        genre = Genre(name="Original", categories=set_categories)
        genre_repository.save(genre)

        updated = Genre(
            id=genre.id,
            name="Atualizado",
            categories=set_categories,
            is_active=False,
        )

        genre_repository.update(updated)
        persisted = genre_repository.get_by_id(genre.id)

        assert persisted is not None
        assert persisted.id == genre.id
        assert persisted.name == "Atualizado"
        assert persisted.categories == set_categories
        assert persisted.is_active is False

    def test_multiple_updates_keep_only_last(self, genre_repository, set_categories):
        genre = Genre(name="Série", categories=set_categories)
        genre_repository.save(genre)

        update1 = Genre(
            id=genre.id,
            name="Series",
            categories=set_categories,
            is_active=False,
        )
        update2 = Genre(
            id=genre.id,
            name="TV Actions",
            categories=set_categories,
            is_active=True,
        )

        genre_repository.update(update1)
        genre_repository.update(update2)

        updated = genre_repository.get_by_id(genre.id)
        assert updated.name == "TV Actions"
        assert updated.categories == set_categories
        assert updated.is_active is True


# -------------------- Testes de listagem -------------------- #


class TestListGenre:
    def test_list_returns_all_saved_genres(self, genre_repository, set_categories):
        genre1 = Genre(name="Terror", categories=set_categories)
        genre2 = Genre(name="Comédia", categories=set_categories)

        genre_repository.save(genre1)
        genre_repository.save(genre2)

        genres = genre_repository.list()
        assert len(genres) == 2
        assert genre1 in genres
        assert genre2 in genres
