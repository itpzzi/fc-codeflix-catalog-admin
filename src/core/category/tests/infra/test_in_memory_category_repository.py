import uuid
from src.core.category.domain.category import Category
from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)


class TestSave:
    def test_can_save_category(self):
        repository = InMemoryCategoryRepository()
        category = Category(
            name="Filme",
            description="Categoria para filmes",
        )

        repository.save(category)

        assert len(repository.categories) == 1
        assert repository.categories[0] == category


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

        repository = InMemoryCategoryRepository(
            categories=[category_movie, category_show]
        )

        response = repository.get_by_id(category_show.id)

        assert len(repository.categories) == 2
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

        repository = InMemoryCategoryRepository(
            categories=[category_movie, category_show]
        )
        fake_id = uuid.uuid4()

        response = repository.get_by_id(fake_id)

        assert len(repository.categories) == 2
        assert response is None


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

        repository = InMemoryCategoryRepository(
            categories=[category_movie, category_show]
        )

        response = repository.delete(category_movie.id)

        assert len(repository.categories) == 1
        assert response is None
