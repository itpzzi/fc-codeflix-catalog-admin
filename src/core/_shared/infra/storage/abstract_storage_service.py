from abc import ABC, abstractmethod


class AbstractStorageService(ABC):
    @abstractmethod
    def store(self, file_name: str, content_type: str, content: bytes) -> None:
        raise NotImplementedError("store method must be implemented")
