from unittest.mock import MagicMock
from uuid import UUID
import pytest

from src.core.category.application.exceptions import InvalidCategory
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)
from src.core.category.application.usecases.create_category import (
    CreateCategory,
)


class TestCreateCategory:
    def test_create_category_with_valid_data(self):
        repository = MagicMock(ICategoryRepository)
        use_case = CreateCategory(repository=repository)
        input = CreateCategory.Input(name="Filme", description="Filme", is_active=False)

        output = use_case.execute(input=input)

        assert output.id is not None
        assert isinstance(output, CreateCategory.Output)
        assert isinstance(output.id, UUID)
        assert repository.save.called is True

    def test_create_category_with_invalid_data(self):
        repository = MagicMock(ICategoryRepository)
        use_case = CreateCategory(repository=repository)

        with pytest.raises(InvalidCategory, match="name cannot be empty") as exec_info:
            use_case.execute(CreateCategory.Input(name=""))

        assert exec_info.type is InvalidCategory
        assert str(exec_info.value) == "name cannot be empty"
