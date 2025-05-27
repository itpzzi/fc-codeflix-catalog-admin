from abc import ABC, abstractmethod


class AbstractTokenService(ABC):
    algorithm: str
    private_key: str
    public_key: str

    @abstractmethod
    def generate_token(self, payload: dict, expires_in_minutes: int = 60):
        raise NotImplementedError

    @abstractmethod
    def decode_token(self, token: str):
        raise NotImplementedError
