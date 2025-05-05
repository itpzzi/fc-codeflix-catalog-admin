from dataclasses import asdict, dataclass
from uuid import UUID

from src.core.category.application.category_repository import (
    CategoryRepositoryInterface,
)
from src.core.category.application.exceptions import InvalidCategory
from src.core.category.application.exceptions import CategoryNotFound
from src.core.category.domain.category import Category


@dataclass
class GetCategoryRequest:
    id: UUID


@dataclass
class GetCategoryResponse:
    id: UUID
    name: str
    description: str
    is_active: bool


class GetCategoryUseCase:

    def __init__(self, repository: CategoryRepositoryInterface):
        self.repository = repository

    def execute(self, request: GetCategoryRequest) -> GetCategoryResponse:
        repo_cat = self.repository.get_by_id(request.id)
        if repo_cat is None:
            raise CategoryNotFound(f"Category {request.id} not found")

        try:
            category = Category(
                id=repo_cat.id,
                name=repo_cat.name,
                description=repo_cat.description,
                is_active=repo_cat.is_active,
            )
        except ValueError as error:
            raise InvalidCategory(error)

        return GetCategoryResponse(**asdict(category))