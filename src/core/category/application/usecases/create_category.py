from dataclasses import dataclass
from uuid import UUID

from src.core.category.application.exceptions import InvalidCategory
from src.core.category.domain.category import Category
from src.core.category.domain.category_repository import (
    ICategoryRepository,
)


class CreateCategory:

    @dataclass
    class Input:
        name: str
        is_active: bool = True
        description: str = ""

    @dataclass
    class Output:
        id: UUID

    def __init__(self, repository: ICategoryRepository):
        self.repository = repository

    def execute(self, input: Input) -> Output:
        try:
            category = Category(
                name=input.name,
                description=input.description,
                is_active=input.is_active,
            )
        except ValueError as error:
            raise InvalidCategory(error)

        self.repository.save(category)
        return CreateCategory.Output(id=category.id)
