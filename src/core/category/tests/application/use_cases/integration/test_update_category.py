import uuid

from src.core.category.application.usecases.update_category import (
    UpdateCategory,
)
from src.core.category.domain.category import Category
from src.core.category.infra.in_memory_category_repository import (
    InMemoryCategoryRepository,
)


class TestUpdateCategory:
    def test_can_update_category_name_and_description(self):
        mock_category = Category(
            id=uuid.uuid4(),
            name="Desenhos",
            description="Animações para a criançada.",
            is_active=True,
        )
        repository = InMemoryCategoryRepository(categories=[])
        repository.save(mock_category)
        use_case = UpdateCategory(repository=repository)
        input = UpdateCategory.Input(
            id=mock_category.id,
            name="Animações",
            description="Animações para público geral.",
            is_active=False,
        )

        use_case.execute(input=input)

        updated_category = repository.get_by_id(mock_category.id)
        assert updated_category is not None
        assert updated_category.name == "Animações"
        assert updated_category.description == "Animações para público geral."
        assert updated_category.is_active is False
