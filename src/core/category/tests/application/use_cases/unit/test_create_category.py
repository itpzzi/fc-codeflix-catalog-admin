from unittest.mock import MagicMock
from uuid import UUID
import pytest

from src.core.category.application.exceptions import InvalidCategory
from src.core.category.application.category_repository import (
    CategoryRepositoryInterface,
)
from src.core.category.application.usecases.create_category import (
    CreateCategoryRequest,
    CreateCategoryResponse,
    CreateCategoryUseCase,
)


class TestCreateCategory:
    def test_create_category_with_valid_data(self):
        repository = MagicMock(CategoryRepositoryInterface)
        use_case = CreateCategoryUseCase(repository=repository)
        request = CreateCategoryRequest(
            name="Filme", description="Filme", is_active=False
        )

        response = use_case.execute(request=request)

        assert response.id is not None
        assert isinstance(response, CreateCategoryResponse)
        assert isinstance(response.id, UUID)
        assert repository.save.called is True

    def test_create_category_with_invalid_data(self):
        repository = MagicMock(CategoryRepositoryInterface)
        use_case = CreateCategoryUseCase(repository=repository)

        with pytest.raises(InvalidCategory, match="name cannot be empty") as exec_info:
            use_case.execute(CreateCategoryRequest(name=""))

        assert exec_info.type is InvalidCategory
        assert str(exec_info.value) == "name cannot be empty"
