from abc import ABC, abstractmethod


class AbstractJWTAuthService(ABC):
    @abstractmethod
    def is_authenticated(self, token: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def has_role(self, token: str, role: str) -> bool:
        raise NotImplementedError
