from abc import ABC, abstractmethod

from src.core.category.domain.category import Category


class CategoryRepositoryInterface(ABC):
    @abstractmethod
    def save(self, category) -> Category:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, UUID) -> Category | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, category: Category) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Category]:
        raise NotImplementedError
