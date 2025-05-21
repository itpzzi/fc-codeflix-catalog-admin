from src.core._shared.events.abstract_message_bus import AbstractMessageBus
from src.core._shared.events.event import Event


class MessageBus(AbstractMessageBus):
    def handle(self, event_list: list[Event]) -> None:
        pass
