from dataclasses import dataclass
from typing import Generic, TypeVar

from src.core._shared.config import DEFAULT_PAGE_SIZE

T = TypeVar("T")


@dataclass
class MetaData:
    total: int
    current_page: int
    per_page: int


@dataclass
class ListEntityInput:
    order_by: str = "name"
    reverse: bool = False
    current_page: int = 1
    per_page: int = DEFAULT_PAGE_SIZE


class ListEntityOutput(Generic[T]):
    def __init__(self, input_params: ListEntityInput, data: list[T]) -> None:
        self._input = input_params
        self._raw_data = data
        self.meta = MetaData(
            total=len(data),
            current_page=input_params.current_page,
            per_page=input_params.per_page,
        )
        self.data = self._build_output()

    def _build_output(self) -> list[T]:
        ordered_data = self._apply_ordering(self._raw_data)
        paginated_data = self._apply_pagination(ordered_data)
        return paginated_data

    def _apply_ordering(self, data: list[T]) -> list[T]:
        return sorted(
            data,
            key=lambda item: getattr(item, self._input.order_by),
            reverse=self._input.reverse,
        )

    def _apply_pagination(self, data: list[T]) -> list[T]:
        start = (self._input.current_page - 1) * self._input.per_page
        end = start + self._input.per_page
        return data[start:end]
