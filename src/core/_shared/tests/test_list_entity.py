from dataclasses import dataclass

import pytest

from src.core._shared.application.list_entity import (
    ListEntityInput,
    ListEntityOutput,
    MetaData,
)


@dataclass
class MockEntity:
    name: str
    value: int


@pytest.fixture
def mock_entities():
    return [
        MockEntity(name="C", value=3),
        MockEntity(name="A", value=1),
        MockEntity(name="D", value=4),
        MockEntity(name="B", value=2),
    ]


def test_default_ordering_and_pagination(mock_entities):
    input_params = ListEntityInput()
    output = ListEntityOutput(input_params, mock_entities)

    assert [e.name for e in output.data] == ["A", "B"]
    assert output.meta == MetaData(total=4, current_page=1, per_page=2)


def test_reverse_ordering(mock_entities):
    input_params = ListEntityInput(order_by="name", reverse=True, per_page=2)
    output = ListEntityOutput(input_params, mock_entities)

    assert [e.name for e in output.data] == ["D", "C"]


def test_order_by_different_field(mock_entities):
    input_params = ListEntityInput(order_by="value", reverse=False, per_page=4)
    output = ListEntityOutput(input_params, mock_entities)

    assert [e.value for e in output.data] == [1, 2, 3, 4]


def test_pagination_second_page(mock_entities):
    input_params = ListEntityInput(order_by="name", current_page=2, per_page=2)
    output = ListEntityOutput(input_params, mock_entities)

    assert [e.name for e in output.data] == ["C", "D"]
    assert output.meta.current_page == 2
    assert output.meta.per_page == 2
    assert output.meta.total == 4


def test_empty_list():
    input_params = ListEntityInput()
    output = ListEntityOutput(input_params, [])

    assert output.data == []
    assert output.meta.total == 0
    assert output.meta.current_page == 1
    assert output.meta.per_page == 2
