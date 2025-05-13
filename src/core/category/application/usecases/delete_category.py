from dataclasses import dataclass
from uuid import UUID

from src.core.category.domain.category_repository import (
    ICategoryRepository,
)
from src.core.category.application.exceptions import CategoryNotFound, InvalidCategory
from src.core.category.domain.category import Category


@dataclass
class DeleteCategoryInput:
    id: UUID


class DeleteCategoryUseCase:

    def __init__(self, repository: ICategoryRepository):
        self.repository = repository

    def execute(self, request: DeleteCategoryInput) -> None:
        category_from_repo = self.repository.get_by_id(request.id)

        if category_from_repo is None:
            raise CategoryNotFound(
                f"Cannot delete non-existent category. {request.id} not found"
            )

        self.repository.delete(category_from_repo.id)
