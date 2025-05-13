from dataclasses import dataclass
from uuid import UUID

from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)


class DeleteCategory:

    @dataclass
    class Input:
        id: UUID

    def __init__(self, repository: ICategoryRepository):
        self.repository = repository

    def execute(self, input: Input) -> None:
        category_from_repo = self.repository.get_by_id(input.id)

        if category_from_repo is None:
            raise CategoryNotFound(
                f"Cannot delete non-existent category. {input.id} not found"
            )

        self.repository.delete(category_from_repo.id)
