import uuid
import pytest
from src.core.genre.domain.genre import Genre
from src.django_project.genre_app.repository import DjangoORMGenreRepository
from src.django_project.category_app.repository import DjangoORMCategoryRepository
from src.django_project.category_app.models import Category
from src.django_project.genre_app.models import Genre as GenreModel


@pytest.fixture
def genre_repository():
    return DjangoORMGenreRepository()


@pytest.fixture
def category_repository():
    return DjangoORMCategoryRepository()


@pytest.fixture
def categories(category_repository):
    movie = Category(name="Filme", description="Categoria para filmes")
    show = Category(name="Show", description="Espetáculos")
    category_repository.save(movie)
    category_repository.save(show)
    return movie, show


@pytest.fixture
def genre_with_categories(categories):
    movie, show = categories
    return Genre(name="Infantil", categories={movie.id, show.id})


@pytest.fixture
def genre_repository_with_genre(genre_repository, genre_with_categories):
    genre_repository.save(genre_with_categories)
    return genre_repository


@pytest.mark.django_db
class TestSave:
    def test_can_save_genre(
        self, genre_repository, category_repository, categories, genre_with_categories
    ):
        movie, show = categories
        genre = genre_with_categories

        assert len(genre_repository.list()) == 0
        genre_repository.save(genre)
        assert len(genre_repository.list()) == 1

        saved = genre_repository.get_by_id(genre.id)
        assert saved.id == genre.id
        assert saved.name == genre.name
        assert saved.categories == {movie.id, show.id}
        assert saved.is_active is True
        assert saved.id is not None


@pytest.mark.django_db
class TestGet:
    def test_can_get_by_id_with_related_categories(
        self, genre_repository_with_genre, genre_with_categories, categories
    ):
        movie, show = categories
        genre = genre_with_categories

        saved = genre_repository_with_genre.get_by_id(genre.id)
        assert len(genre_repository_with_genre.list()) == 1
        assert saved.id == genre.id
        assert saved.name == genre.name
        assert saved.categories == {movie.id, show.id}
        assert saved.is_active is True
        assert saved.id is not None

    def test_return_none_for_non_existent_id(self, genre_repository_with_genre):
        fake_id = uuid.uuid4()

        saved = genre_repository_with_genre.get_by_id(fake_id)
        assert len(genre_repository_with_genre.list()) == 1
        assert saved is None


@pytest.mark.django_db
class TestDelete:
    def test_can_delete_genre(self, genre_repository_with_genre, genre_with_categories):

        assert len(genre_repository_with_genre.list()) == 1

        genre_repository_with_genre.delete(genre_with_categories.id)

        assert len(genre_repository_with_genre.list()) == 0
        assert genre_repository_with_genre.get_by_id(genre_with_categories.id) is None


@pytest.mark.django_db
class TestUpdate:
    def test_can_update_genre(self, genre_repository_with_genre, genre_with_categories):
        assert len(genre_repository_with_genre.list()) == 1
        to_update_genre = Genre(
            id=genre_with_categories.id,
            name="Family",
            is_active=False,
            categories=set(),
        )

        genre_repository_with_genre.update(to_update_genre)
        updated_genre = genre_repository_with_genre.get_by_id(genre_with_categories.id)

        assert updated_genre is not None
        assert len(genre_repository_with_genre.list()) == 1
        assert updated_genre.id == to_update_genre.id
        assert updated_genre.name == to_update_genre.name
        assert updated_genre.categories == to_update_genre.categories
        assert updated_genre.is_active == to_update_genre.is_active

    def test_update_nonexistent_genre_does_nothing(
        self, genre_repository_with_genre, genre_with_categories
    ):
        fake_id = uuid.uuid4()
        to_update_genre = Genre(
            id=fake_id, name="Family", is_active=False, categories=set()
        )

        genre_repository_with_genre.update(to_update_genre)
        not_updated_genre = genre_repository_with_genre.get_by_id(
            genre_with_categories.id
        )

        assert not_updated_genre is not None
        assert len(genre_repository_with_genre.list()) == 1
        assert not_updated_genre.id == genre_with_categories.id
        assert not_updated_genre.name == genre_with_categories.name
        assert not_updated_genre.categories == genre_with_categories.categories
        assert not_updated_genre.is_active == genre_with_categories.is_active

    def test_update_preserves_id(
        self, genre_with_categories, genre_repository_with_genre
    ):
        to_update_genre = Genre(
            id=genre_with_categories.id,
            name="Family",
            is_active=False,
            categories=set(),
        )

        genre_repository_with_genre.update(to_update_genre)
        updated_genre = genre_repository_with_genre.get_by_id(genre_with_categories.id)

        assert updated_genre is not None
        assert len(genre_repository_with_genre.list()) == 1
        assert updated_genre.id == genre_with_categories.id

    def test_multiple_updates_keep_only_last(
        self, genre_with_categories, genre_repository_with_genre
    ):
        _1st_to_update_genre = Genre(
            id=genre_with_categories.id,
            name="Only Children",
            is_active=True,
            categories=set(),
        )
        _2nd_to_update_genre = Genre(
            id=genre_with_categories.id,
            name="Family",
            is_active=False,
            categories=set(),
        )

        genre_repository_with_genre.update(_1st_to_update_genre)
        genre_repository_with_genre.update(_2nd_to_update_genre)
        updated_genre = genre_repository_with_genre.get_by_id(genre_with_categories.id)

        assert updated_genre is not None
        assert len(genre_repository_with_genre.list()) == 1
        assert updated_genre.id == _2nd_to_update_genre.id
        assert updated_genre.name == _2nd_to_update_genre.name
        assert updated_genre.categories == _2nd_to_update_genre.categories
        assert updated_genre.is_active == _2nd_to_update_genre.is_active


@pytest.mark.django_db
class TestList:
    def test_list_all_genres(self, genre_repository_with_genre, genre_with_categories):
        genre = genre_with_categories

        genres = genre_repository_with_genre.list()

        assert len(genres) == 1
        assert genres == [
            Genre(
                id=genre.id,
                name=genre.name,
                categories=genre.categories,
                is_active=genre.is_active,
            )
        ]

    def test_retuns_empty_list_for_empty_repository(self, genre_repository):
        genres = genre_repository.list()

        assert len(genres) == 0
        assert genres == []
