from src.core.category.domain.category import Category
from src.django_project.category_app.models import Category as CategoryModel


class CategoryModelMapper:
    @staticmethod
    def to_entity(model: CategoryModel) -> Category:
        return Category(
            id=model.id,
            name=model.name,
            is_active=model.is_active,
            description=model.description,
        )

    @staticmethod
    def to_model(category: Category) -> CategoryModel:
        model = CategoryModel(
            id=category.id,
            name=category.name,
            is_active=category.is_active,
            description=category.description,
        )
        return model
