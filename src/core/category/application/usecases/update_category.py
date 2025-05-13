from dataclasses import dataclass
from uuid import UUID

from src.core.category.domain.category_repository import (
    ICategoryRepository,
)
from src.core.category.application.exceptions import CategoryNotFound, InvalidCategory
from src.core.category.domain.category import Category


@dataclass
class UpdateCategoryInput:
    id: UUID
    name: str | None = None
    description: str | None = None
    is_active: bool | None = None


class UpdateCategoryUseCase:

    def __init__(self, repository: ICategoryRepository):
        self.repository = repository

    def execute(self, request: UpdateCategoryInput) -> None:
        category_from_repo = self.repository.get_by_id(request.id)

        if category_from_repo is None:
            raise CategoryNotFound(
                f"Cannot update non-existent category. {request.id} not found"
            )

        current_name = category_from_repo.name
        current_description = category_from_repo.description
        current_is_active = category_from_repo.is_active

        if request.name is not None:
            current_name = request.name

        if request.description is not None:
            current_description = request.description

        if request.is_active is not None:
            current_is_active = request.is_active

        category_from_repo.update_category(
            name=current_name, description=current_description
        )

        if current_is_active is True:
            category_from_repo.activate()

        if current_is_active is False:
            category_from_repo.deactivate()

        self.repository.update(category_from_repo)
