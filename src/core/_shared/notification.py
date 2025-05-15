class Notification:
    def __init__(self) -> None:
        self._errors: list[str] = []

    def add_error(self, message: str):
        self._errors.append(message)

    @property
    def has_errors(self) -> bool:
        return len(self._errors) > 0

    @property
    def messages(self) -> str:
        return "; ".join(self._errors)

    def clear(self):
        self._errors.clear()

    def __len__(self):
        return len(self._errors)

    def __str__(self) -> str:
        return self.messages
