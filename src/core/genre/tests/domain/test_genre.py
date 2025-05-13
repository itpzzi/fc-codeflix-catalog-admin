import uuid
from uuid import UUID

import pytest

from src.core.genre.domain.genre import Genre

# -------------------- Fixtures -------------------- #


@pytest.fixture
def genre():
    return Genre(name="Filmes")


@pytest.fixture
def inactive_genre():
    return Genre(name="Filmes", is_active=False)


@pytest.fixture
def category_uuids():
    return uuid.uuid4(), uuid.uuid4()


# -------------------- Testes de criação -------------------- #


class TestGenreCreation:
    def test_requires_name_argument(self):
        with pytest.raises(
            TypeError, match="missing 1 required positional argument: 'name'"
        ):
            Genre()

    def test_rejects_name_longer_than_255_chars(self):
        with pytest.raises(ValueError, match="name cannot be longer than 255"):
            Genre(name="a" * 256)

    def test_creates_genre_with_default_values(self, genre):
        assert genre.name == "Filmes"
        assert isinstance(genre.id, UUID)
        assert genre.categories == set()
        assert genre.is_active is True

    def test_creates_genre_with_explicit_values(self):
        gid = uuid.uuid4()
        cat1, cat2 = uuid.uuid4(), uuid.uuid4()

        g = Genre(name="Filme", categories={cat1, cat2}, id=gid, is_active=False)

        assert g.name == "Filme"
        assert g.categories == {cat1, cat2}
        assert g.id == gid
        assert g.is_active is False

    def test_rejects_empty_name(self):
        with pytest.raises(ValueError, match="name cannot be empty"):
            Genre(name="")


# -------------------- Testes de mudança de nome -------------------- #


class TestChangeName:
    def test_valid_name_update(self, genre):
        original = Genre(
            name=genre.name,
            categories=set(genre.categories),
            is_active=genre.is_active,
            id=genre.id,
        )
        genre.change_name("Movie")

        assert genre.name == "Movie"
        assert genre.id == original.id
        assert original.name == "Filmes"
        assert genre.name != original.name

    def test_rejects_invalid_name_too_long(self, genre):
        with pytest.raises(ValueError, match="name cannot be longer than 255"):
            genre.change_name("a" * 256)

    def test_rejects_empty_name(self, genre):
        with pytest.raises(ValueError, match="name cannot be empty"):
            genre.change_name("")


# -------------------- Testes de ativação -------------------- #


class TestActivate:
    def test_activates_inactive_genre(self, inactive_genre):
        inactive_genre.activate()
        assert inactive_genre.is_active is True

    def test_activating_already_active_genre_is_idempotent(self, genre):
        genre.activate()
        assert genre.is_active is True


# -------------------- Testes de desativação -------------------- #


class TestDeactivate:
    def test_deactivates_active_genre(self, genre):
        genre.deactivate()
        assert genre.is_active is False

    def test_deactivating_already_inactive_genre_is_idempotent(self, inactive_genre):
        inactive_genre.deactivate()
        assert inactive_genre.is_active is False


# -------------------- Testes de igualdade -------------------- #


class TestEquality:
    def test_genres_with_same_id_are_equal(self):
        gid = uuid.uuid4()
        g1 = Genre(id=gid, name="A")
        g2 = Genre(id=gid, name="B")
        assert g1 == g2

    def test_equality_with_different_class_returns_false(self):
        class Dummy:
            pass

        g = Genre(id=uuid.uuid4(), name="Filme")
        dummy = Dummy()
        dummy.id = g.id

        assert g != dummy


# -------------------- Testes de categoria -------------------- #


class TestAddCategory:
    def test_adds_multiple_categories(self, genre, category_uuids):
        cat1, cat2 = category_uuids

        assert len(genre.categories) == 0

        genre.add_category(cat1)
        assert genre.categories == {cat1}

        genre.add_category(cat2)
        assert genre.categories == {cat1, cat2}

    def test_adds_same_category_only_once(self, genre):
        cat = uuid.uuid4()
        genre.add_category(cat)
        genre.add_category(cat)
        assert len(genre.categories) == 1


class TestRemoveCategory:
    def test_removes_existing_category(self, genre, category_uuids):
        cat1, cat2 = category_uuids
        genre.add_category(cat1)
        genre.add_category(cat2)

        genre.remove_category(cat1)
        assert genre.categories == {cat2}

        genre.remove_category(cat2)
        assert genre.categories == set()

    def test_raises_on_removing_nonexistent_category(self, genre):
        cat = uuid.uuid4()
        with pytest.raises(KeyError):
            genre.remove_category(cat)
