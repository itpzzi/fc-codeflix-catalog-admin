from abc import ABC, abstractmethod

from src.core.genre.domain.genre import Genre


class IGenreRepository(ABC):
    @abstractmethod
    def save(self, genre) -> Genre:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, UUID) -> Genre | None:
        raise NotImplementedError

    @abstractmethod
    def delete(self, UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def update(self, genre: Genre) -> None:
        raise NotImplementedError

    @abstractmethod
    def list(self) -> list[Genre]:
        raise NotImplementedError
