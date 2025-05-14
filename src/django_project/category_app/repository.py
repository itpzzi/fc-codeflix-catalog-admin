from uuid import UUID

from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import ICategoryRepository
from src.django_project.category_app.mapper import CategoryModelMapper
from src.django_project.category_app.models import Category as CategoryModel


class DjangoORMCategoryRepository(ICategoryRepository):
    def __init__(self, model: CategoryModel = CategoryModel):
        self.model = model

    def save(self, category: Category) -> None:
        self.model.objects.create(
            id=category.id,
            name=category.name,
            description=category.description,
            is_active=category.is_active,
        )

    def get_by_id(self, id: UUID) -> Category | None:
        try:
            model = self.model.objects.get(id=id)
            return CategoryModelMapper.to_entity(model)
        except self.model.DoesNotExist:
            return None

    def delete(self, id: UUID) -> None:
        self.model.objects.filter(id=id).delete()

    def update(self, category: Category) -> None:
        self.model.objects.filter(pk=category.id).update(
            name=category.name,
            description=category.description,
            is_active=category.is_active,
        )

    def list(self) -> list[Category]:
        return [
            CategoryModelMapper.to_entity(model) for model in self.model.objects.all()
        ]
