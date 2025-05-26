from dataclasses import asdict
from typing import Generic, Type, TypeVar

T = TypeVar("T")


class Deserializer(Generic[T]):
    def __init__(self, data: dict, dto_class: Type[T]):
        self.data = data
        self.dto_class = dto_class
        self._validated_data: T | None = None
        self._errors: Exception | None = None

    def is_valid(self, raise_exception: bool = False) -> bool:
        try:
            internal_data = self.to_internal()
            self._validated_data = self.dto_class(**internal_data)
            return True
        except Exception as e:
            self._errors = e
            if raise_exception:
                raise
            return False

    def to_internal(self) -> dict:
        return self.data

    @property
    def validated_data(self) -> dict:
        if self._validated_data is None:
            raise ValueError(
                "You must call is_valid() before accessing validated_data."
            )
        return asdict(self._validated_data)

    @property
    def instance(self) -> T:
        if self._validated_data is None:
            raise ValueError("You must call is_valid() before accessing instance.")
        return self._validated_data
