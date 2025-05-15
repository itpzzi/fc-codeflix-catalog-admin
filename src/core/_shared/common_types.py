class Name(str):
    def __new__(cls, value: str):
        if not value:
            raise ValueError("name cannot be empty")
        if len(value) > 255:
            raise ValueError("name cannot be longer than 255 characters")
        return super().__new__(cls)


class CheckSum(str):
    def __new__(cls, value: str):
        if not value:
            raise ValueError("checksum cannot be empty")
        if len(value) < 32 or len(value) > 64:
            raise ValueError("checksum must be between 32 and 64 characters")
        return super().__new__(cls, value)


class Location(str):
    def __new__(cls, value: str):
        if not value:
            raise ValueError("location cannot be empty")
        if not value.startswith("http") and not value.startswith("/"):
            raise ValueError("location must be a valid path or URL")
        return super().__new__(cls, value)
