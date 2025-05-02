from dataclasses import dataclass
from uuid import UUID

from src.core.category.application.category_repository import (
    CategoryRepositoryInterface,
)
from src.core.category.application.exceptions import InvalidCategory
from src.core.category.domain.category import Category


@dataclass
class CreateCategoryRequest:
    name: str
    is_active: bool = True
    description: str = ""


@dataclass
class CreateCategoryResponse:
    id: UUID


class CreateCategoryUseCase:

    def __init__(self, repository: CategoryRepositoryInterface):
        self.repository = repository

    def execute(self, request: CreateCategoryRequest) -> CreateCategoryResponse:
        try:
            category = Category(
                name=request.name,
                description=request.description,
                is_active=request.is_active,
            )
        except ValueError as error:
            raise InvalidCategory(error)

        self.repository.save(category)
        return CreateCategoryResponse(id=category.id)
