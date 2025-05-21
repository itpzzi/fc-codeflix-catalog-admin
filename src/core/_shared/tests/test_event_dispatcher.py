from unittest.mock import Mock, create_autospec

import pytest

from src.core._shared.events.event import IntegrationEvent
from src.core._shared.events.event_dispatcher import EventDispatcher


class DummyDispatchableEvent(IntegrationEvent):
    pass


@pytest.fixture
def dummy_event():
    return DummyDispatchableEvent()


@pytest.fixture
def dispatcher_mock():
    return create_autospec(EventDispatcher, instance=True)


@pytest.fixture
def handler_mock(dispatcher_mock):
    handler = Mock()
    handler.handle = Mock(side_effect=lambda event: dispatcher_mock.dispatch(event))
    return handler


def test_handler_delegates_to_dispatcher(handler_mock, dispatcher_mock, dummy_event):
    handler_mock.handle(dummy_event)
    dispatcher_mock.dispatch.assert_called_once_with(dummy_event)
