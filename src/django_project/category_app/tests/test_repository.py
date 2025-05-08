import uuid
import pytest
from src.django_project.category_app.repository import DjangoORMCategoryRepository
from src.django_project.category_app.models import Category


@pytest.mark.django_db
class TestSave:
    def test_can_save_category(self):
        category = Category(
            name="Filme",
            description="Longas divertidos",
        )
        repository = DjangoORMCategoryRepository()

        assert len(repository.list()) == 0
        repository.save(category)
        assert len(repository.list()) == 1

        saved_category = repository.get_by_id(category.id)
        assert saved_category.id == category.id
        assert saved_category.name == category.name
        assert saved_category.description == category.description
        assert saved_category.is_active is True
        assert saved_category.id is not None


@pytest.mark.django_db
class TestGet:
    def test_can_get_by_id(self):
        category_movie = Category(
            name="Filme",
            description="Categoria para filmes",
        )
        category_show = Category(
            name="Show",
            description="Espetaculos",
        )

        repository = DjangoORMCategoryRepository()
        repository.save(category_movie)
        repository.save(category_show)

        response = repository.get_by_id(category_show.id)

        assert len(repository.list()) == 2
        assert response.id == category_show.id
        assert response.name == "Show"
        assert response.description == "Espetaculos"
        assert response.is_active is True

    def test_return_none_for_non_existent_id(self):
        category_movie = Category(
            name="Filme",
            description="Categoria para filmes",
        )
        category_show = Category(
            name="Show",
            description="Espetaculos",
        )

        repository = DjangoORMCategoryRepository()
        repository.save(category_movie)
        repository.save(category_show)

        fake_id = uuid.uuid4()

        response = repository.get_by_id(fake_id)

        assert len(repository.list()) == 2
        assert response is None


@pytest.mark.django_db
class TestDelete:
    def test_can_delete_category(self):
        category_movie = Category(
            name="Filme",
            description="Categoria para filmes",
        )
        category_show = Category(
            name="Show",
            description="Espetaculos",
        )

        repository = DjangoORMCategoryRepository()
        repository.save(category_movie)
        repository.save(category_show)

        assert len(repository.list()) == 2

        repository.delete(category_show.id)

        assert len(repository.list()) == 1
        assert repository.get_by_id(category_show.id) is None


@pytest.mark.django_db
class TestUpdate:
    def test_can_update_category(self):
        category_movie = Category(
            name="Filme",
            description="Categoria para filmes",
        )
        category_show = Category(
            name="Show",
            description="Espetaculos",
        )

        repository = DjangoORMCategoryRepository()
        repository.save(category_movie)
        repository.save(category_show)

        updated_category = Category(
            id=category_show.id,
            name="Show Atualizado",
            description="Espetaculos Atualizados",
        )

        repository.update(updated_category)

        response = repository.get_by_id(category_show.id)

        assert len(repository.list()) == 2
        assert response.id == updated_category.id
        assert response.name == "Show Atualizado"
        assert response.description == "Espetaculos Atualizados"

    def test_update_nonexistent_category_does_nothing(self):
        category_movie = Category(
            name="Filme",
            description="Categoria para filmes",
        )
        category_show = Category(
            name="Show",
            description="Espetaculos",
        )

        repository = DjangoORMCategoryRepository()
        repository.save(category_movie)
        repository.save(category_show)

        fake_id = uuid.uuid4()

        updated_category = Category(
            id=fake_id,
            name="Show Atualizado",
            description="Espetaculos Atualizados",
        )

        repository.update(updated_category)

        response = repository.get_by_id(category_show.id)

        assert len(repository.list()) == 2
        assert response.id == category_show.id
        assert response.name == "Show"
        assert response.description == "Espetaculos"

    def test_update_preserves_id(self):
        category_movie = Category(
            name="Filme",
            description="Categoria para filmes",
        )
        category_show = Category(
            name="Show",
            description="Espetaculos",
        )

        repository = DjangoORMCategoryRepository()
        repository.save(category_movie)
        repository.save(category_show)

        updated_category = Category(
            id=category_show.id,
            name="Show Atualizado",
            description="Espetaculos Atualizados",
        )

        repository.update(updated_category)

        response = repository.get_by_id(category_show.id)

        assert len(repository.list()) == 2
        assert response.id == updated_category.id

    def test_multiple_updates_keep_only_last(self):
        category_movie = Category(
            name="Filme",
            description="Categoria para filmes",
        )
        category_show = Category(
            name="Show",
            description="Espetaculos",
        )

        repository = DjangoORMCategoryRepository()
        repository.save(category_movie)
        repository.save(category_show)

        updated_category_1 = Category(
            id=category_show.id,
            name="Show Atualizado 1",
            description="Espetaculos Atualizados 1",
        )

        updated_category_2 = Category(
            id=category_show.id,
            name="Show Atualizado 2",
            description="Espetaculos Atualizados 2",
        )

        repository.update(updated_category_1)
        repository.update(updated_category_2)

        response = repository.get_by_id(category_show.id)

        assert len(repository.list()) == 2
        assert response.id == updated_category_2.id
        assert response.name == "Show Atualizado 2"


@pytest.mark.django_db
class TestList:
    def test_list_all_categories(self):
        category_movie = Category(
            name="Filme",
            description="Categoria para filmes",
        )
        category_show = Category(
            name="Show",
            description="Espetaculos",
        )

        repository = DjangoORMCategoryRepository()
        repository.save(category_movie)
        repository.save(category_show)

        response = repository.list()

        assert len(response) == 2
        assert response[0].id == category_movie.id
        assert response[1].id == category_show.id
