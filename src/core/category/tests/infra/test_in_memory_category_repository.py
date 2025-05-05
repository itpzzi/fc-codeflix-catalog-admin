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


class TestUpdate:
    def test_can_update_category(self):
        category_movie = Category(
            name="Filme",
            description="Categoria para filmes",
        )
        repository = InMemoryCategoryRepository(categories=[])
        repository.save(category_movie)
        assert len(repository.categories) == 1
        repository_category = repository.get_by_id(category_movie.id)

        repository.update(
            Category(
                id=repository_category.id,
                name="Movie",
                description="Category for movies",
                is_active=False,
            )
        )

        assert len(repository.categories) == 1
        assert repository.categories[0].name == "Movie"
        assert repository.categories[0].description == "Category for movies"
        assert repository.categories[0].is_active is False

    def test_update_nonexistent_category_does_nothing(self):
        repository = InMemoryCategoryRepository()
        new_category = Category(
            id=uuid.uuid4(),
            name="Documentário",
            description="Categoria para documentários",
        )

        repository.update(new_category)

        assert len(repository.categories) == 0

    def test_update_preserves_id(self):
        category = Category(name="Original", description="Descrição original")
        repo = InMemoryCategoryRepository([category])

        updated = Category(
            id=category.id,
            name="Atualizado",
            description="Nova descrição",
            is_active=False,
        )

        repo.update(updated)
        persisted = repo.get_by_id(category.id)

        assert persisted is not None
        assert persisted.id == category.id  # ID deve se manter
        assert persisted.name == "Atualizado"
        assert persisted.description == "Nova descrição"
        assert persisted.is_active is False

    def test_update_overwrites_previous_data(self):
        original = Category(
            name="Esporte", description="Tudo sobre esportes", is_active=True
        )
        repo = InMemoryCategoryRepository([original])

        modified = Category(
            id=original.id,
            name="Sports",
            description="All about sports",
            is_active=False,
        )
        repo.update(modified)

        result = repo.get_by_id(original.id)
        assert result.name == "Sports"
        assert result.description == "All about sports"
        assert result.is_active is False

    def test_multiple_updates_keep_only_last(self):
        category = Category(name="Série", description="Categoria")
        repo = InMemoryCategoryRepository([category])

        update1 = Category(
            id=category.id,
            name="Series",
            description="Primeira atualização",
            is_active=False,
        )
        update2 = Category(
            id=category.id,
            name="TV Shows",
            description="Segunda atualização",
            is_active=True,
        )

        repo.update(update1)
        repo.update(update2)

        updated = repo.get_by_id(category.id)
        assert updated.name == "TV Shows"
        assert updated.description == "Segunda atualização"
        assert updated.is_active is True
