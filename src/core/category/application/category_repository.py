from abc import ABC, abstractmethod

from src.core.category.domain.category import Category


class CategoryRepositoryInterface(ABC):
    @abstractmethod
    def save(self, category) -> Category:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, UUID) -> Category | None:
        raise NotImplementedError
