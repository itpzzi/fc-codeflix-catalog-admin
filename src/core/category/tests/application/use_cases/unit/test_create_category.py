from unittest.mock import MagicMock
from uuid import UUID
import pytest

from src.core.category.application.exceptions import InvalidCategory
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)
from src.core.category.application.usecases.create_category import (
    CreateCategoryInput,
    CreateCategoryOutput,
    CreateCategoryUseCase,
)


class TestCreateCategory:
    def test_create_category_with_valid_data(self):
        repository = MagicMock(ICategoryRepository)
        use_case = CreateCategoryUseCase(repository=repository)
        request = CreateCategoryInput(
            name="Filme", description="Filme", is_active=False
        )

        response = use_case.execute(request=request)

        assert response.id is not None
        assert isinstance(response, CreateCategoryOutput)
        assert isinstance(response.id, UUID)
        assert repository.save.called is True

    def test_create_category_with_invalid_data(self):
        repository = MagicMock(ICategoryRepository)
        use_case = CreateCategoryUseCase(repository=repository)

        with pytest.raises(InvalidCategory, match="name cannot be empty") as exec_info:
            use_case.execute(CreateCategoryInput(name=""))

        assert exec_info.type is InvalidCategory
        assert str(exec_info.value) == "name cannot be empty"
