class Name(str):
    def __new__(cls, value: str):
        if not value:
            raise ValueError("name cannot be empty")
        if len(value) > 255:
            raise ValueError("name cannot be longer than 255 characters")
        return super().__new__(cls)
