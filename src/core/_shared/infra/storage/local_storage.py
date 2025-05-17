from pathlib import Path

from src.core._shared.infra.storage.abstract_storage_service import (
    AbstractStorageService,
)


class LocalStorage(AbstractStorageService):
    TMP_PATH = Path("/tmp/codeflix-storage")

    def __init__(self, bucket: Path = TMP_PATH):
        self.bucket = bucket

    def store(self, file_name: str, content_type: str, content: bytes) -> None:
        path = self.bucket / file_name
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(content)
