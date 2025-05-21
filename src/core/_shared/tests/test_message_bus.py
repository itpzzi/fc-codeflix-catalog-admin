from unittest.mock import create_autospec

import pytest

from src.core._shared.application.handlers import EventHandler
from src.core._shared.events.event import Event
from src.core._shared.events.message_bus import MessageBus


class DummyEvent(Event):
    pass


class DummyEventHandler(EventHandler[DummyEvent]):
    def handle(self, event: DummyEvent) -> None:
        pass


class ExceptionEventHandler(EventHandler[DummyEvent]):
    def handle(self, event: DummyEvent) -> None:
        raise Exception("Test exception")


@pytest.fixture
def message_bus():
    return MessageBus()


@pytest.fixture
def mock_handler():
    return create_autospec(DummyEventHandler)


class TestHandle:
    def test_register_handler(self, message_bus):

        handler = DummyEventHandler()
        event_type = DummyEvent

        message_bus.register_handler(event_type, handler)

        assert len(message_bus.handlers) == 1
        assert event_type in message_bus.handlers
        assert handler in message_bus.handlers[event_type]

    def test_unregister_handler(self, message_bus):
        handler = DummyEventHandler()
        event = DummyEvent()
        event_type = type(event)

        message_bus.register_handler(event_type, handler)
        assert len(message_bus.handlers) == 1
        assert event_type in message_bus.handlers
        assert handler in message_bus.handlers[event_type]

        message_bus.unregister_handler(event_type, handler)
        assert event_type not in message_bus.handlers

    def test_handle(self, message_bus, mock_handler):
        event = DummyEvent()
        event_type = type(event)

        message_bus.register_handler(event_type, mock_handler)

        message_bus.handle([event])

        mock_handler.handle.assert_called_once_with(event)

    def test_handle_multiple_events(self, message_bus):

        handler1 = create_autospec(DummyEventHandler)
        handler2 = create_autospec(DummyEventHandler)
        event1 = DummyEvent()
        event2 = DummyEvent()

        message_bus.register_handler(type(event1), handler1)
        message_bus.register_handler(type(event2), handler2)
        message_bus.handle([event1, event2])

        handler1.handle.assert_any_call(event1)
        handler1.handle.assert_any_call(event2)
        handler2.handle.assert_any_call(event1)
        handler2.handle.assert_any_call(event2)
        assert handler1.handle.call_count == 2
        assert handler2.handle.call_count == 2

    def test_handle_multiple_handlers_for_event(self, message_bus):

        handler1 = create_autospec(DummyEventHandler)
        handler2 = create_autospec(DummyEventHandler)
        event = DummyEvent()
        event_type = type(event)

        message_bus.register_handler(event_type, handler1)
        message_bus.register_handler(event_type, handler2)
        message_bus.handle([event])

        handler1.handle.assert_called_once_with(event)
        handler2.handle.assert_called_once_with(event)

    def test_handle_no_handlers_registered(self, message_bus):

        event = DummyEvent()

        message_bus.handle([event])

    def test_handle_exception_in_handler(self, message_bus, caplog):

        handler = ExceptionEventHandler()
        regular_handler = create_autospec(DummyEventHandler)
        event = DummyEvent()
        event_type = type(event)

        message_bus.register_handler(event_type, handler)
        message_bus.register_handler(event_type, regular_handler)
        message_bus.handle([event])

        regular_handler.handle.assert_called_once_with(event)

        assert "Error handling DummyEvent" in caplog.text
