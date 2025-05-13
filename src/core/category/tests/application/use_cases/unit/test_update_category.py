from unittest.mock import create_autospec
import uuid
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)
from src.core.category.application.usecases.update_category import (
    UpdateCategoryInput,
    UpdateCategoryUseCase,
)
from src.core.category.domain.category import Category


class TestUpdateCategory:
    def test_update_category_name(self):
        mock_category = Category(
            id=uuid.uuid4(),
            name="Filme",
            description="Categoria para filmes",
            is_active=True,
        )
        mock_repository = create_autospec(ICategoryRepository)
        mock_repository.get_by_id.return_value = mock_category

        use_case = UpdateCategoryUseCase(repository=mock_repository)
        request = UpdateCategoryInput(id=mock_category.id, name="Série")

        use_case.execute(request)

        assert mock_category.name == "Série"
        assert mock_category.description == "Categoria para filmes"
        mock_repository.update.assert_called_once_with(mock_category)

    def test_update_category_description(self):
        mock_category = Category(
            id=uuid.uuid4(),
            name="Filme",
            description="Categoria para filmes",
            is_active=True,
        )
        mock_repository = create_autospec(ICategoryRepository)
        mock_repository.get_by_id.return_value = mock_category

        use_case = UpdateCategoryUseCase(repository=mock_repository)
        request = UpdateCategoryInput(
            id=mock_category.id, description="Categoria para séries"
        )

        use_case.execute(request)

        assert mock_category.name == "Filme"
        assert mock_category.description == "Categoria para séries"
        mock_repository.update.assert_called_once_with(mock_category)

    def test_can_deactivate_category(self):
        mock_category = Category(
            id=uuid.uuid4(),
            name="Filme",
            description="Categoria para filmes",
            is_active=True,
        )
        mock_repository = create_autospec(ICategoryRepository)
        mock_repository.get_by_id.return_value = mock_category

        use_case = UpdateCategoryUseCase(repository=mock_repository)
        request = UpdateCategoryInput(id=mock_category.id, is_active=False)

        use_case.execute(request)

        assert mock_category.name == "Filme"
        assert mock_category.is_active is False
        assert mock_category.description == "Categoria para filmes"
        mock_repository.update.assert_called_once_with(mock_category)

    def test_can_activate_category(self):
        mock_category = Category(
            id=uuid.uuid4(),
            name="Filme",
            description="Categoria para filmes",
            is_active=False,
        )
        mock_repository = create_autospec(ICategoryRepository)
        mock_repository.get_by_id.return_value = mock_category

        use_case = UpdateCategoryUseCase(repository=mock_repository)
        request = UpdateCategoryInput(id=mock_category.id, is_active=True)

        use_case.execute(request)

        assert mock_category.name == "Filme"
        assert mock_category.is_active is True
        assert mock_category.description == "Categoria para filmes"
        mock_repository.update.assert_called_once_with(mock_category)
