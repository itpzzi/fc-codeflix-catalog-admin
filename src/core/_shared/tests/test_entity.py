from unittest.mock import create_autospec

from src.core._shared.domain.entity import Entity
from src.core._shared.events.abstract_message_bus import AbstractMessageBus
from src.core._shared.events.event import Event


class DummyEvent(Event):
    pass


class DummyEntity(Entity):
    def validate(self):
        pass


class TestDispatch:

    def test_dispatch(self):
        message_bus = create_autospec(AbstractMessageBus)
        dummy_event = DummyEvent()
        dummy_entity = DummyEntity(message_bus=message_bus)
        dummy_entity.dispatch(dummy_event)
        assert len(dummy_entity.events) == 1
        message_bus.handle.assert_called_once_with([dummy_event])
